from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAdjust': {'Parameters': ['Device ID'], 'Status': {}},
            'ImageOrientation': {'Parameters': ['Device ID'], 'Status': {}},
            'LEDBlueIntensity': {'Parameters': ['Device ID', 'Color'], 'Status': {}},
            'LEDDayMode': {'Parameters': ['Device ID'], 'Status': {}},
            'LEDGreenIntensity': {'Parameters': ['Device ID', 'Color'], 'Status': {}},
            'LEDMainIntensity': {'Parameters': ['Device ID', 'Color'], 'Status': {}},
            'LEDNightMode': {'Parameters': ['Device ID'], 'Status': {}},
            'LEDRedIntensity': {'Parameters': ['Device ID', 'Color'], 'Status': {}},
            'OperationHours': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.respRegex = {
                'AutoAdjust': re.compile(b'DATA\(([0-9]{1,3});COLOR_AUTOADJUST;(0|1)\)|NACK\(([0-9]{1,3})\)'),
                'ImageOrientation': re.compile(b'DATA\(([0-9]{1,3});IMAGE_ORIENTATION;(0|1|2|3)\)|NACK\(([0-9]{1,3})\)'),
                'LEDMainIntensity': re.compile(b'DATA\(([0-9]{1,3});LED_INTENSITY_(BLUE_B|GREEN_G|RED_R);([0-9]{1,4})\)|NACK\(([0-9]{1,3})\)'),
                'LEDBlueIntensity': re.compile(b'DATA\(([0-9]{1,3});LED_INTENSITY_(BLUE_R|BLUE_G);([0-9]{1,4})\)|NACK\(([0-9]{1,3})\)'),
                'LEDGreenIntensity': re.compile(b'DATA\(([0-9]{1,3});LED_INTENSITY_(GREEN_B|GREEN_R);([0-9]{1,4})\)|NACK\(([0-9]{1,3})\)'),
                'LEDRedIntensity': re.compile(b'DATA\(([0-9]{1,3});LED_INTENSITY_(RED_B|RED_G);([0-9]{1,4})\)|NACK\(([0-9]{1,3})\)'),
                'Power': re.compile(b'DATA\(([0-9]{1,3});POWER;(0|1)\)|NACK\(([0-9]{1,3})\)'),
                'OperationHours': re.compile(b'DATA\(([0-9]{1,3});INFO_ON_TIME;(\d+)\)|NACK\(([0-9]{1,3})\)'),
                'ErrorCheck' : re.compile(b'NACK\(([0-9]{1,3})\)')
            }

    def SetAutoAdjust(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 0 <= qualifier['Device ID'] <= 999:
            AutoAdjustCmdString = 'SET({0};COLOR_AUTOADJUST;{1})'.format(qualifier['Device ID'], ValueStateValues[value])
            self.__SetHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAdjust')

    def UpdateAutoAdjust(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if 1 <= qualifier['Device ID'] <= 999:
            AutoAdjustCmdString = 'GET({0};COLOR_AUTOADJUST)'.format(qualifier['Device ID']).encode()
            res = self.__UpdateHelper('AutoAdjust', AutoAdjustCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['AutoAdjust'], res)
                    value = ValueStateValues[match.group(2).decode()]
                    self.WriteStatus('AutoAdjust', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['AutoAdjust: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAutoAdjust')

    def SetImageOrientation(self, value, qualifier):

        ValueStateValues = {
            'Rear': '0',
            'Front': '1',
            'Ceiling': '2',
            'Floor': '3'
        }

        if 0 <= qualifier['Device ID'] <= 999:
            ImageOrientationCmdString = 'SET({0};IMAGE_ORIENTATION;{1})'.format(qualifier['Device ID'], ValueStateValues[value])
            self.__SetHelper('ImageOrientation', ImageOrientationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageOrientation')

    def UpdateImageOrientation(self, value, qualifier):

        ValueStateValues = {
            '0': 'Rear',
            '1': 'Front',
            '2': 'Ceiling',
            '3': 'Floor'
        }
        if 1 <= qualifier['Device ID'] <= 999:
            ImageOrientationCmdString = 'GET({0};IMAGE_ORIENTATION)'.format(qualifier['Device ID']).encode()
            res = self.__UpdateHelper('ImageOrientation', ImageOrientationCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['ImageOrientation'], res)
                    value = ValueStateValues[match.group(2).decode()]
                    self.WriteStatus('ImageOrientation', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['ImageOrientation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateImageOrientation')

    def SetLEDBlueIntensity(self, value, qualifier):

        if 0 <= qualifier['Device ID'] <= 999 and 0 <= value <= 1023:
            ColorStateValues = {
                'Red': 'SET({0};LED_Intensity_BLUE_R;{1})'.format(qualifier['Device ID'], value),
                'Green': 'SET({0};LED_Intensity_BLUE_G;{1})'.format(qualifier['Device ID'], value)
            }

            LEDBlueIntensityCmdString = ColorStateValues[qualifier['Color']]
            self.__SetHelper('LEDBlueIntensity', LEDBlueIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDBlueIntensity')

    def UpdateLEDBlueIntensity(self, value, qualifier):

        ColorStates = {
            'Red': 'BLUE_R',
            'Green': 'BLUE_G',
        }

        if 1 <= qualifier['Device ID'] <= 999:
            LEDBlueIntensityCmdString = 'GET({0};LED_INTENSITY_{1})'.format(qualifier['Device ID'], ColorStates[qualifier['Color']]).encode()
            res = self.__UpdateHelper('LEDBlueIntensity', LEDBlueIntensityCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['LEDBlueIntensity'], res)
                    value = int(match.group(3).decode())
                    self.WriteStatus('LEDBlueIntensity', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['LEDBlueIntensity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLEDBlueIntensity')

    def SetLEDDayMode(self, value, qualifier):

        if 0 <= qualifier['Device ID'] <= 999:
            LEDDayModeCmdString = 'SET({0};LED_INTENSITY_GREEN_G;1000) SET({0};LED_INTENSITY_BLUE_B;1000) SET({0};LED_INTENSITY_RED_R;1000)'.format(qualifier['Device ID'])
            self.__SetHelper('LEDDayMode', LEDDayModeCmdString, value, qualifier)
        else:
        	self.Discard('Invalid Command for SetLEDDayMode')

    def SetLEDGreenIntensity(self, value, qualifier):

        if 0 <= qualifier['Device ID'] <= 999 and 0 <= value <= 1023:
            ColorStateValues = {
                'Red': 'SET({0};LED_Intensity_GREEN_R;{1})'.format(qualifier['Device ID'], value),
                'Blue': 'SET({0};LED_Intensity_GREEN_B;{1})'.format(qualifier['Device ID'], value)
            }
            LEDGreenIntensityCmdString = ColorStateValues[qualifier['Color']]
            self.__SetHelper('LEDGreenIntensity', LEDGreenIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDGreenIntensity')

    def UpdateLEDGreenIntensity(self, value, qualifier):

        ColorStates = {
            'Red': 'GREEN_R',
            'Blue': 'GREEN_B',
        }

        if 1 <= qualifier['Device ID'] <= 999:
            LEDGreenIntensityCmdString = 'GET({0};LED_INTENSITY_{1})'.format(qualifier['Device ID'], ColorStates[qualifier['Color']]).encode()
            res = self.__UpdateHelper('LEDGreenIntensity', LEDGreenIntensityCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['LEDGreenIntensity'], res)
                    value = int(match.group(3).decode())
                    self.WriteStatus('LEDGreenIntensity', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['LEDGreenIntensity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLEDGreenIntensity')

    def SetLEDMainIntensity(self, value, qualifier):

        ColorStates = {
            'Red': 'RED_R',
            'Green': 'GREEN_G',
            'Blue': 'BLUE_B'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 1023
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 0 <= qualifier['Device ID'] <= 999:
            LEDMainIntensityCmdString = 'SET({0};LED_INTENSITY_{1};{2})'.format(qualifier['Device ID'], ColorStates[qualifier['Color']], value)
            self.__SetHelper('LEDMainIntensity', LEDMainIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDMainIntensity')

    def UpdateLEDMainIntensity(self, value, qualifier):

        ColorStates = {
            'Red': 'RED_R',
            'Green': 'GREEN_G',
            'Blue': 'BLUE_B'
        }

        if 1 <= qualifier['Device ID'] <= 999:
            LEDMainIntensityCmdString = 'GET({0};LED_INTENSITY_{1})'.format(qualifier['Device ID'], ColorStates[qualifier['Color']]).encode()
            res = self.__UpdateHelper('LEDMainIntensity', LEDMainIntensityCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['LEDMainIntensity'], res)
                    value = int(match.group(3).decode())
                    self.WriteStatus('LEDMainIntensity', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['LEDMainIntensity: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLEDMainIntensity')

    def SetLEDNightMode(self, value, qualifier):

        if 0 <= qualifier['Device ID'] <= 999:
            LEDNightModeCmdString = 'SET({0};LED_INTENSITY_GREEN_G;100) SET({0};LED_INTENSITY_BLUE_B;100) SET({0};LED_INTENSITY_RED_R;100)'.format(qualifier['Device ID'])
            self.__SetHelper('LEDNightMode', LEDNightModeCmdString, value, qualifier)
        else:
        	self.Discard('Invalid Command for SetLEDNightMode')

    def SetLEDRedIntensity(self, value, qualifier):

        if 0 <= qualifier['Device ID'] <= 999 and 0 <= value <= 1023:
            ColorStateValues = {
                'Green': 'SET({0};LED_Intensity_RED_G;{1})'.format(qualifier['Device ID'], value),
                'Blue': 'SET({0};LED_Intensity_RED_B;{1})'.format(qualifier['Device ID'], value)
            }

            LEDRedIntensityCmdString = ColorStateValues[qualifier['Color']]
            self.__SetHelper('LEDRedIntensity', LEDRedIntensityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLEDRedIntensity')

    def UpdateLEDRedIntensity(self, value, qualifier):

        ColorStates = {
            'Green': 'RED_G',
            'Blue': 'RED_B',
        }

        if 1 <= qualifier['Device ID'] <= 999:
            LEDRedIntensityCmdString = 'GET({0};LED_INTENSITY_{1})'.format(qualifier['Device ID'], ColorStates[qualifier['Color']]).encode()
            res = self.__UpdateHelper('LEDRedIntensity', LEDRedIntensityCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['LEDRedIntensity'], res)
                    value = int(match.group(3).decode())
                    self.WriteStatus('LEDRedIntensity', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['LEDRedIntensity: Invalid/unexpected response'])

        else:
            self.Discard('Invalid Command for UpdateLEDRedIntensity')

    def UpdateOperationHours(self, value, qualifier):

        if 1 <= qualifier['Device ID'] <= 999:
            OperationHoursCmdString = 'GET({0};INFO_ON_TIME)'.format(qualifier['Device ID']).encode()
            res = self.__UpdateHelper('OperationHours', OperationHoursCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['OperationHours'], res)
                    value = int(match.group(2).decode())
                    self.WriteStatus('OperationHours', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    self.Error(['OperationHours: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOperationHours')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 0 <= qualifier['Device ID'] <= 999:
            PowerCmdString = 'SET({0};POWER;{1})'.format(qualifier['Device ID'], ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        if 1 <= qualifier['Device ID'] <= 999:
            PowerCmdString = 'GET({0};POWER)'.format(qualifier['Device ID']).encode()
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    match = re.search(self.respRegex['Power'], res)
                    value = ValueStateValues[match.group(2).decode()]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if b'NAK(' in response:
            self.counter = 0
            self.Error(['Device responded with an error for command or query: {}'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command in self.respRegex:
                rexToUse = self.respRegex[command]
            else:
                rexToUse = self.respRegex['ErrorCheck']
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=rexToUse)
            if not res:
                self.Error(['Set{}: Unexpected/Invalid response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.respRegex[command])
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':', res)

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

