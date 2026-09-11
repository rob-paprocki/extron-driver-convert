from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}
        self._DeviceID = '00'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Backlight': {'Status': {}},
            'Brightness': {'Status': {}},
            'Input': {'Status': {}},
            'PIP': {'Status': {}},
            'PIPHorizontalPosition': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'PIPVerticalPosition': {'Status': {}},
            'Power': {'Status': {}},
            }

        self.setRegex = re.compile(b'\x15|\x06')
        self.updateRegex = re.compile(b'\x06[\x00-\xff]{1,2}\.|\x15')

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if 0 <= int(value) <= 255:
            self._DeviceID = '{0:02d}'.format(int(value))

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = 'did:all-{0}-faa.'.format(self._DeviceID)
        chk = 0
        for val in AutoImageCmdString:
            chk = chk ^ ord(val)
        AutoImageCmdString = AutoImageCmdString + chr(chk)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BacklightCmdString = 'did:all-{0}-B{1:02X}.'.format(self._DeviceID, value)
            chk = 0
            for val in BacklightCmdString:
                chk = chk ^ ord(val)
            BacklightCmdString = BacklightCmdString + chr(chk)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        BacklightCmdString = 'did:all-{0}-sbl.'.format(self._DeviceID)
        chk = 0
        for val in BacklightCmdString:
            chk = chk ^ ord(val)
        BacklightCmdString = BacklightCmdString + chr(chk)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:3], 16)
                self.WriteStatus('Backlight', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateBacklight')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BrightnessCmdString = 'did:all-{0}-b{1:02X}.'.format(self._DeviceID, value)
            chk = 0
            for val in BrightnessCmdString:
                chk = chk ^ ord(val)
            BrightnessCmdString = BrightnessCmdString + chr(chk)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        BrightnessCmdString = 'did:all-{0}-sbr.'.format(self._DeviceID)
        chk = 0
        for val in BrightnessCmdString:
            chk = chk ^ ord(val)
        BrightnessCmdString = BrightnessCmdString + chr(chk)
        res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1:3], 16)
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateBrightness')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': '4',
            'VGA 2': '5',
            'DVI 1': '1',
            'DVI 2': '2',
            'DVI 3': '3',
            'CVBS 1': '6',
            'CVBS 2': '7',
            'CVBS 3': '8',
        }

        InputCmdString = 'did:all-{0}-mn{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in InputCmdString:
            chk = chk ^ ord(val)
        InputCmdString = InputCmdString + chr(chk)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '4': 'VGA 1',
            '5': 'VGA 2',
            '1': 'DVI 1',
            '2': 'DVI 2',
            '3': 'DVI 3',
            '6': 'CVBS 1',
            '7': 'CVBS 2',
            '8': 'CVBS 3',
        }

        InputCmdString = 'did:all-{0}-sms.'.format(self._DeviceID)
        chk = 0
        for val in InputCmdString:
            chk = chk ^ ord(val)
        InputCmdString = InputCmdString + chr(chk)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if res[1] == '0':
                    value = ValueStateValues[res[2]]
                else:
                    value = ValueStateValues[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }
        PIPCmdString = 'did:all-{0}-at{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PIPCmdString:
            chk = chk ^ ord(val)
        PIPCmdString = PIPCmdString + chr(chk)
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def UpdatePIP(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        PIPCmdString = 'did:all-{0}-sat.'.format(self._DeviceID)
        chk = 0
        for val in PIPCmdString:
            chk = chk ^ ord(val)
        PIPCmdString = PIPCmdString + chr(chk)
        res = self.__UpdateHelper('PIP', PIPCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PIP', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIP')

    def SetPIPHorizontalPosition(self, value, qualifier):

        ValueStateValues = {
            'Left': '0',
            'Middle': '1',
            'Right': '2'
        }
        PIPHorizontalPositionCmdString = 'did:all-{0}-ah{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PIPHorizontalPositionCmdString:
            chk = chk ^ ord(val)
        PIPHorizontalPositionCmdString = PIPHorizontalPositionCmdString + chr(chk)
        self.__SetHelper('PIPHorizontalPosition', PIPHorizontalPositionCmdString, value, qualifier)

    def UpdatePIPHorizontalPosition(self, value, qualifier):

        ValueStateValues = {
            '0': 'Left',
            '1': 'Middle',
            '2': 'Right'
        }
        PIPHorizontalPositionCmdString = 'did:all-{0}-sah.'.format(self._DeviceID)
        chk = 0
        for val in PIPHorizontalPositionCmdString:
            chk = chk ^ ord(val)
        PIPHorizontalPositionCmdString = PIPHorizontalPositionCmdString + chr(chk)
        res = self.__UpdateHelper('PIPHorizontalPosition', PIPHorizontalPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PIPHorizontalPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPHorizontalPosition')

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'VGA 1': '4',
            'VGA 2': '5',
            'DVI 1': '1',
            'DVI 2': '2',
            'DVI 3': '3',
            'CVBS 1': '6',
            'CVBS 2': '7',
            'CVBS 3': '8',
        }

        PIPInputCmdString = 'did:all-{0}-ax{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PIPInputCmdString:
            chk = chk ^ ord(val)
        PIPInputCmdString = PIPInputCmdString + chr(chk)
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            '4': 'VGA 1',
            '5': 'VGA 2',
            '1': 'DVI 1',
            '2': 'DVI 2',
            '3': 'DVI 3',
            '6': 'CVBS 1',
            '7': 'CVBS 2',
            '8': 'CVBS 3',
        }

        PIPInputCmdString = 'did:all-{0}-sas.'.format(self._DeviceID)
        chk = 0
        for val in PIPInputCmdString:
            chk = chk ^ ord(val)
        PIPInputCmdString = PIPInputCmdString + chr(chk)
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                if res[1] == '0':
                    value = ValueStateValues[res[2]]
                else:
                    value = ValueStateValues[res[1]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPInput')

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': '1',
            'Medium': '2',
            'Large': '3'
        }
        PIPSizeCmdString = 'did:all-{0}-ap{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PIPSizeCmdString:
            chk = chk ^ ord(val)
        PIPSizeCmdString = PIPSizeCmdString + chr(chk)
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        ValueStateValues = {
            '1': 'Small',
            '2': 'Medium',
            '3': 'Large'
        }
        PIPSizeCmdString = 'did:all-{0}-sap.'.format(self._DeviceID)
        chk = 0
        for val in PIPSizeCmdString:
            chk = chk ^ ord(val)
        PIPSizeCmdString = PIPSizeCmdString + chr(chk)
        res = self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PIPSize', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPSize')

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'did:all-{0}-asw.'.format(self._DeviceID)
        chk = 0
        for val in PIPSwapCmdString:
            chk = chk ^ ord(val)
        PIPSwapCmdString = PIPSwapCmdString + chr(chk)
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPIPVerticalPosition(self, value, qualifier):

        ValueStateValues = {
            'Top': '0',
            'Middle': '1',
            'Bottom': '2'
        }
        PIPVerticalPositionCmdString = 'did:all-{0}-av{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PIPVerticalPositionCmdString:
            chk = chk ^ ord(val)
        PIPVerticalPositionCmdString = PIPVerticalPositionCmdString + chr(chk)
        self.__SetHelper('PIPVerticalPosition', PIPVerticalPositionCmdString, value, qualifier)

    def UpdatePIPVerticalPosition(self, value, qualifier):

        ValueStateValues = {
            '0': 'Top',
            '1': 'Middle',
            '2': 'Bottom'
        }
        PIPVerticalPositionCmdString = 'did:all-{0}-sav.'.format(self._DeviceID)
        chk = 0
        for val in PIPVerticalPositionCmdString:
            chk = chk ^ ord(val)
        PIPVerticalPositionCmdString = PIPVerticalPositionCmdString + chr(chk)
        res = self.__UpdateHelper('PIPVerticalPosition', PIPVerticalPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('PIPVerticalPosition', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePIPVerticalPosition')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        PowerCmdString = 'did:all-{0}-pw{1}.'.format(self._DeviceID, ValueStateValues[value])
        chk = 0
        for val in PowerCmdString:
            chk = chk ^ ord(val)
        PowerCmdString = PowerCmdString + chr(chk)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        PowerCmdString = 'did:all-{0}-spw.'.format(self._DeviceID)
        chk = 0
        for val in PowerCmdString:
            chk = chk ^ ord(val)
        PowerCmdString = PowerCmdString + chr(chk)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == '\x15':
            print('Device responded with an error.')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.setRegex)
            if not res:
                print('Invalid/Unexpected Response')
            else:
                self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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
