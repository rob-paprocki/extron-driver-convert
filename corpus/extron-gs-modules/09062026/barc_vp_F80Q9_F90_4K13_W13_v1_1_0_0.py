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
            'Focus': {'Parameters':['Steps'], 'Status': {}},
            'Illumination': { 'Status': {}},
            'Input': { 'Status': {}},
            'LensShift': {'Parameters':['Steps'], 'Status': {}},
            'Power': { 'Status': {}},
            'Shutter': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'TestPatternSelect': { 'Status': {}},
            'Zoom': {'Parameters':['Steps'], 'Status': {}},
            }






        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?300,[\r\n ]*"result": ?(100|[0-9]{1,2})\.?0?[\r\n ]*}', re.I), self.__MatchIllumination, None)
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?130,[\r\n ]*"result": ?"?(Ready|On)"?[\r\n ]*}', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?423,[\r\n ]*"result": ?"(DVI [12]|DisplayPort [12]|HDMI|HDBaseT|SDI)"[\r\n ]*}', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?141,[\r\n ]*"result": ?"?(true|false)"?[\r\n ]*}', re.I), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?147,[\r\n ]*"result": ?"internal:([A-Za-z ]*)"[\r\n ]*}', re.I), self.__MatchTestPatternSelect, None)
            self.AddMatchString(re.compile(b'{[\r\n ]*"jsonrpc": ?"2\.0",[\r\n ]*"id": ?([0-9]*),[\r\n ]*"error": ?{[\r\n ]*"code": ?(-?[0-9]*), ?"message": ?"([\s\S]*)"}[\r\n ]*}', re.I), self.__MatchError, None)





    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'In' : 'forward', 
            'Out' : 'reverse'
        }
        
        Steps = qualifier['Steps']
        if str(Steps).isdigit():
            if value == 'Stop':
                FocusCmdString = '{"jsonrpc": "2.0","method": "optics.focus.stop","params": {},"id": 470}\r\n'
            else:
                FocusCmdString = ''.join(['{"jsonrpc": "2.0", "method": "optics.focus.step', ValueStateValues[value], '", "params": {"steps": ', str(Steps), '}, "id": 470}\r\n'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')



    def SetIllumination(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IlluminationCmdString = ''.join(['{"jsonrpc": "2.0","method": "property.set","id": 300,"params": {"property": "illumination.sources.laser.power","value": ', str(value), '}}\r\n'])
            self.__SetHelper('Illumination', IlluminationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIllumination')
    def UpdateIllumination(self, value, qualifier):

        IlluminationCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "illumination.sources.laser.power"},"id": 300}\r\n'
        self.__UpdateHelper('Illumination', IlluminationCmdString, value, qualifier)

    def __MatchIllumination(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Illumination', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = ['DVI 1', 'DVI 2', 'DisplayPort 1', 'DisplayPort 2', 'HDMI', 'HDBaseT', 'SDI']
        
        if value in ValueStateValues:
            InputCmdString = ''.join(['{"jsonrpc": "2.0","method": "property.set","params": {"property": "image.window.main.source", "value": "', value, '"},"id": 423}\r\n'])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')
    def UpdateInput(self, value, qualifier):

        InputCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "image.window.main.source"},"id": 423}\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'dvi 1'         : 'DVI 1', 
            'dvi 2'         : 'DVI 2', 
            'displayport 1' : 'DisplayPort 1', 
            'displayport 2' : 'DisplayPort 2', 
            'hdmi'          : 'HDMI', 
            'hdbaset'       : 'HDBaseT', 
            'sdi'           : 'SDI'
        }
        
        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Input', value, None)

    def SetLensShift(self, value, qualifier):

        ValueStateValues = {
            'Up'    : 'vertical.stepreverse', 
            'Down'  : 'vertical.stepforward', 
            'Left'  : 'horizontal.stepreverse', 
            'Right' : 'horizontal.stepforward'
        }

        Steps = qualifier['Steps']
        if str(Steps).isdigit():
            if value == 'Stop':
                LensShiftCmdString = '{"jsonrpc": "2.0","method": "optics.lensshift.stop","params": {},"id": 2356}\r\n'
            else:
                LensShiftCmdString = ''.join(['{"jsonrpc": "2.0", "method": "optics.lensshift.', ValueStateValues[value], '", "params": {"steps": ', str(Steps), '}, "id": 2356}\r\n'])
            self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLensShift')
            


    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }
        
        PowerCmdString = ''.join(['{"jsonrpc": "2.0","method": "system.power', ValueStateValues[value], '","params": {},"id": 130}\r\n'])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):


        PowerCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "system.state"},"id": 130}\r\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on'    : 'On', 
            'ready' : 'Off',
        }


        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('Power', value, None)

    def SetShutter(self, value, qualifier):

        ShutterCmdString = '{"jsonrpc": "2.0","method": "optics.shutter.toggle","params": {},"id": 310}\r\n'
        self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)



    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true', 
            'Off' : 'false'
        }

        TestPatternCmdString = ''.join(['{"jsonrpc": "2.0","method": "property.set","id": 141,"params": {"property": "image.testpattern.show", "value": ', ValueStateValues[value], '}}\r\n'])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "image.testpattern.show"},"id": 141}\r\n'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            'true' : 'On', 
            'false' : 'Off'
        }
        value = ValueStateValues[match.group(1).decode().lower()]
        self.WriteStatus('TestPattern', value, None)

    def SetTestPatternSelect(self, value, qualifier):

        ValueStateValues = ['Focus Black', 'Ansi Lumen', 'Scenergix', 'Checker Board', 'Focus', 'Cross Hatch', 'Monoscope', 'Outline', 'Color Bars', 'Aspect']

        if value in ValueStateValues:
            TestPatternSelectCmdString = ''.join(['{"jsonrpc": "2.0","method": "property.set","id": 147,"params": {"property": "image.testpattern.selected", "value": "internal:', value, '"}}\r\n'])
            self.__SetHelper('TestPatternSelect', TestPatternSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPatternSelect')
    def UpdateTestPatternSelect(self, value, qualifier):

        TestPatternSelectCmdString = '{"jsonrpc": "2.0","method": "property.get","params": {"property": "image.testpattern.selected"},"id": 147}\r\n'
        self.__UpdateHelper('TestPatternSelect', TestPatternSelectCmdString, value, qualifier)

    def __MatchTestPatternSelect(self, match, tag):

        ValueStateValues = {
            'focus black'   : 'Focus Black', 
            'ansi lumen'    : 'Ansi Lumen', 
            'scenergix'     : 'Scenergix', 
            'checker board' : 'Checker Board', 
            'focus'         : 'Focus', 
            'cross hatch'   : 'Cross Hatch', 
            'monoscope'     : 'Monoscope', 
            'outline'       : 'Outline', 
            'color bars'    : 'Color Bars', 
            'aspect'        : 'Aspect'
        }
        
        if match.group(1).decode().lower() in ValueStateValues:
            value = ValueStateValues[match.group(1).decode().lower()]
            self.WriteStatus('TestPatternSelect', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In'  : 'forward', 
            'Out' : 'reverse'
        }

        Steps = qualifier['Steps']
        if str(Steps).isdigit():
            if value == 'Stop':
                ZoomCmdString = '{"jsonrpc": "2.0","method": "optics.zoom.stop","params": {},"id": 450}\r\n'
            else:
                ZoomCmdString = ''.join(['{"jsonrpc": "2.0", "method": "optics.zoom.step', ValueStateValues[value], '", "params": {"steps": ', str(Steps), '}, "id": 450}'])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



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

            self.Send(commandstring)



    def __MatchError(self, match, tag):

        self.Error(['Error number {0} occured: {1}'.format(match.group(2).decode(),match.group(3).decode())])

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

