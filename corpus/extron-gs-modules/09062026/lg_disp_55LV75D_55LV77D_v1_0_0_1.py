from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'AspectRatio': {'Parameters':['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters':['Device ID'], 'Status': {}},
            'EnergySaving': {'Parameters':['Device ID'], 'Status': {}},
            'Input': {'Parameters':['Device ID'], 'Status': {}},
            'Keypad': {'Parameters':['Device ID'], 'Status': {}},
            'MenuNavigation': {'Parameters':['Device ID'], 'Status': {}},
            'NaturalMode': {'Parameters':['Device ID'], 'Status': {}},
            'Power': {'Parameters':['Device ID'], 'Status': {}},
            'TileMode': {'Parameters':['Device ID','Column','Row'], 'Status': {}},
            'TilePosition': {'Parameters':['Device ID','Tile ID'], 'Status': {}},
            'VideoMute': {'Parameters':['Device ID'], 'Status': {}},
            }                    

        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'q ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchEnergySaving, None)
            self.AddMatchString(re.compile(b'b ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'j ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchNaturalMode, None)
            self.AddMatchString(re.compile(b'a ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'd ([0-9A-F]{2,3}) OK([0-9A-F]{2})x',re.I), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'(i|j|c|b|a|d|f|q) ([0-9A-F]{2,3}) NG(.*?)x',re.I), self.__MatchError, None)

        self.regexSet = re.compile(b'(OK|NG)[0-9A-F]{2}x')
    
    def GetDeviceID(self, ID):

        if ID == 'Broadcast':
            return '00'
        elif 1 <= int(ID) <= 255:
            return '{0:02X}'.format(int(ID))
        else:
            self.Error(['Invalid Device ID provided'])

    def SetAspectRatio(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            '4:3'            : '01', 
            '16:9'           : '02', 
            'Zoom'           : '04', 
            'Auto'           : '06', 
            'Original'       : '09', 
            'Cinema Zoom 1'  : '10', 
            'Cinema Zoom 2'  : '11', 
            'Cinema Zoom 3'  : '12', 
            'Cinema Zoom 4'  : '13', 
            'Cinema Zoom 5'  : '14', 
            'Cinema Zoom 6'  : '15', 
            'Cinema Zoom 7'  : '16', 
            'Cinema Zoom 8'  : '17', 
            'Cinema Zoom 9'  : '18', 
            'Cinema Zoom 10' : '19', 
            'Cinema Zoom 11' : '1A', 
            'Cinema Zoom 12' : '1B', 
            'Cinema Zoom 13' : '1C', 
            'Cinema Zoom 14' : '1D', 
            'Cinema Zoom 15' : '1E', 
            'Cinema Zoom 16' : '1F'
        }

        self.__SetHelper('AspectRatio', 'kc {0} {1}\r'.format(ID,States[value]) , value, qualifier)
        
    def UpdateAspectRatio(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('AspectRatio', 'kc {0} FF\r'.format(ID) , value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        States = {
            '01' : '4:3', 
            '02' : '16:9', 
            '04' : 'Zoom', 
            '06' : 'Auto', 
            '09' : 'Original', 
            '10' : 'Cinema Zoom 1', 
            '11' : 'Cinema Zoom 2', 
            '12' : 'Cinema Zoom 3', 
            '13' : 'Cinema Zoom 4', 
            '14' : 'Cinema Zoom 5', 
            '15' : 'Cinema Zoom 6', 
            '16' : 'Cinema Zoom 7', 
            '17' : 'Cinema Zoom 8', 
            '18' : 'Cinema Zoom 9', 
            '19' : 'Cinema Zoom 10', 
            '1A' : 'Cinema Zoom 11', 
            '1B' : 'Cinema Zoom 12', 
            '1C' : 'Cinema Zoom 13', 
            '1D' : 'Cinema Zoom 14', 
            '1E' : 'Cinema Zoom 15', 
            '1F' : 'Cinema Zoom 16'
        }       

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 255:
            self.WriteStatus('AspectRatio',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def SetAutoImage(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__SetHelper('AutoImage', 'ju {0} 01\r'.format(ID) , value, qualifier)

    def SetEnergySaving(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'Off'           : '00', 
            'Minimum'       : '01', 
            'Medium'        : '02', 
            'Maximum'       : '03', 
            'Automatic'     : '04', 
            'Screen Off'    : '05'
        }

        CmdString = 'jq {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('EnergySaving', CmdString, value, qualifier)
        
    def UpdateEnergySaving(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('EnergySaving', 'jq {0} FF\r'.format(ID) , value, qualifier)

    def __MatchEnergySaving(self, match, tag):

        States = {
            '00' : 'Off', 
            '01' : 'Minimum', 
            '02' : 'Medium', 
            '03' : 'Maximum', 
            '04' : 'Automatic', 
            '05' : 'Screen Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 255:
            self.WriteStatus('EnergySaving',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def SetInput(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'RGB'                   : '60', 
            'DVI-D (PC)'            : '70', 
            'DVI-D (DTV)'           : '80', 
            'HDMI (DTV)'            : '90', 
            'OPS (DTV)'             : '91', 
            'HDMI (PC)'             : 'A0', 
            'OPS (PC)'              : 'A1', 
            'DisplayPort (DTV)'     : 'C0', 
            'DisplayPort (PC)'      : 'D0'
        }

        CmdString = 'xb {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)
        
    def UpdateInput(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('Input', 'xb {0} FF\r'.format(ID) , value, qualifier)

    def __MatchInput(self, match, tag):

        States = {
            '60' : 'RGB', 
            '70' : 'DVI-D (PC)', 
            '80' : 'DVI-D (DTV)', 
            '90' : 'HDMI (DTV)', 
            '91' : 'OPS (DTV)', 
            'A0' : 'HDMI (PC)', 
            'A1' : 'OPS (PC)', 
            'C0' : 'DisplayPort (DTV)', 
            'D0' : 'DisplayPort (PC)'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 255:
            self.WriteStatus('Input',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def SetKeypad(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            '0' : '10',
            '1' : '11',
            '2' : '12',
            '3' : '13',
            '4' : '14',
            '5' : '15',
            '6' : '16',
            '7' : '17',
            '8' : '18',
            '9' : '19'       
        }

        CmdString = 'mc {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'Up'        : '40', 
            'Down'      : '41', 
            'Left'      : '07', 
            'Right'     : '06', 
            'Enter'     : '44', 
            'Return'    : '28', 
            'Exit'      : '5B', 
            'S.Menu'    : '3F',
            'Settings'  :'43'
        }

        CmdString = 'mc {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetNaturalMode(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'dj {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('NaturalMode', CmdString, value, qualifier)
        
    def UpdateNaturalMode(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('NaturalMode', 'dj {0} FF\r'.format(ID) , value, qualifier)

    def __MatchNaturalMode(self, match, tag):

        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 255:
            self.WriteStatus('NaturalMode',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def SetPower(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'ka {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)
        
    def UpdatePower(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('Power', 'ka {0} FF\r'.format(ID) , value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        ID = int(match.group(1).decode(), 16)

        if 1 <= int(ID) <= 255:
            self.WriteStatus('Power',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def SetTileMode(self, value, qualifier):

        ID  = self.GetDeviceID(qualifier['Device ID'])
        Col = int(qualifier['Column']) if 0 <= int(qualifier['Column']) <= 50 else ''
        Row = int(qualifier['Row']) if 0 <= int(qualifier['Row']) <= 50 else ''

        if Col and Row:
            Value = '{0:X}{1:X}'.format(Col,Row)
            CmdString = 'dd {0} {1}\r'.format(ID, Value)
            self.__SetHelper('TileMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMode')

    def SetTilePosition(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])
        TileID = int(qualifier['Tile ID'])

        if 1 <= TileID <= 225:
            CmdString = 'di {0} {1:02X}\r'.format(ID, TileID)
            self.__SetHelper('TilePosition', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetVideoMute(self, value, qualifier):

        ID = self.GetDeviceID(qualifier['Device ID'])

        States = {
            'On'  : '01', 
            'Off' : '00'
        }

        CmdString = 'kd {0} {1}\r'.format(ID,States[value])
        self.__SetHelper('VideoMute', CmdString, value, qualifier)
        
    def UpdateVideoMute(self, value, qualifier):
        ID = self.GetDeviceID(qualifier['Device ID'])
        self.__UpdateHelper('VideoMute', 'kd {0} FF\r'.format(ID) , value, qualifier)

    def __MatchVideoMute(self, match, tag):
 
        States = {
            '01' : 'On', 
            '00' : 'Off'
        }

        ID = int(match.group(1).decode(), 16)
        if 1 <= int(ID) <= 255:
            self.WriteStatus('VideoMute',  States[match.group(2).decode()] , {'Device ID' : str(ID)})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if isinstance(response, bytes):
            response = response.decode()

        if 'OK' in response:
            return response
        elif 'NG' in response:
            self.Error(['Error occured in {}'.format(sourceCmdName)])
            return ''

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regexSet)
            if not res:
                self.Error(['{} : Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif command not in ['MasterPower'] and 'Broadcast' in [qualifier['Device ID']]:
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)            

    def __MatchError(self, match, tag):

        State = {
            'i' : 'Tile Position',
            'c' : 'Aspect Ratio, Menu Navigation or Keypad',
            'b' : 'Input',
            'a' : 'Power',
            'j' : 'Natural Mode',
            'q' : 'Energy Saving',
            'd' : 'Video Mute, Tile Mode',
            'f' : 'Volume',
        }
        
        temp1 = State[match.group(1).decode().lower()]
        temp2 = match.group(2).decode().upper()
        temp3 = match.group(3).decode()
        value = '{0} Error, Device ID {1}: {2}'.format(temp1,temp2,temp3)
        self.Error([value])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

