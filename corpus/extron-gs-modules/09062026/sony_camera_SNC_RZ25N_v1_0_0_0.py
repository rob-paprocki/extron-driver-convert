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
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'AutoFocus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Iris': {'Status': {}},
            'Mute': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Preset'], 'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}}
            }        

    def SetFocus(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        ValueStateValues = {
            'Far': 32,
            'Near': 48
        }
        if SpeedConstraints['Min'] <= qualifier['Speed'] <= SpeedConstraints['Max']:
            if value == 'Stop':
                FocusCmdString = b'\x81\x01\x04\x08\x00\xff'
            else:
                FocusCmdString = b'\x81\x01\x04\x08' + pack('>B', ValueStateValues[value] + qualifier['Speed']) + b'\xff'
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x81\x01\x04\x38\x02\xff',
            'Off': b'\x81\x01\x04\x38\x03\xff'
        }

        AutoFocusCmdString = ValueStateValues[value]
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            3: 'Off'
        }

        AutoFocusCmdString = b'\x81\x09\x04\x38\xff'
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAutoFocus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x81\x01\x04\x62\x02\xFF',
            'Off': b'\x81\x01\x04\x62\x03\xFF'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            3: 'Off'
        }

        FreezeCmdString = b'\x81\x09\x04\x62\xff'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateFreeze')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x81\x01\x04\x0b\x00\xff',
            'Down': b'\x81\x01\x04\x0b\x02\xff',
            'Reset': b'\x81\x01\x04\x0b\x03\xff'
        }

        IrisCmdString = ValueStateValues[value]
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x81\x01\x04\x75\x02\xff',
            'Off': b'\x81\x01\x04\x75\x03\xff'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            3: 'Off'
        }

        MuteCmdString = b'\x81\x09\x04\x75\xff'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Mute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMute')

    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 18
            }

        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 17
            }

        ValueStateValues = {
            'Up': b'\x03\x02',
            'Down': b'\x03\x01',
            'Left': b'\x02\x03',
            'Right': b'\x01\x03',
            'Up Left': b'\x02\x02',
            'Up Right': b'\x01\x02',
            'Down Left': b'\x02\x01',
            'Down Right': b'\x01\x01',
            'Stop': b'\x03\x03',
            'Home': b'\x04',
            'Reset': b'\x05'
        }
        if PanSpeedConstraints['Min'] <= qualifier['Pan Speed'] <= PanSpeedConstraints['Max'] and TiltSpeedConstraints['Min'] <= qualifier['Tilt Speed'] <= TiltSpeedConstraints['Max']:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = b'\x81\x01\x06' + ValueStateValues[value] + b'\xff'
            else:
                PanTiltCmdString = b'\x81\x01\x06\x01' + pack('>BB', qualifier['Pan Speed'], qualifier['Tilt Speed']) + ValueStateValues[value] + b'\xff'

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPanTilt')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        PowerCmdString = b'\x81\x09\x7e\x7e\x02\xff'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2] & 1]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePower')

    def SetPreset(self, value, qualifier):

        PresetStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '0': b'\x00'
        }

        ValueStateValues = {
            'Recall': b'\x02',
            'Set': b'\x01',
            'Reset': b'\x00'
        }

        PresetCmdString = b'\x81\x01\x04\x3f' + ValueStateValues[value] + PresetStates[qualifier['Preset']] + b'\xff'
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x35\x00',
            'Indoor': b'\x35\x01',
            'Outdoor': b'\x35\x02',
            'One Push': b'\x35\x03',
            'ATW': b'\x35\x04',
            'Manual': b'\x35\x05',
            'One Push Trigger': b'\x10\x05'
        }

        WhiteBalanceCmdString = b'\x81\x01\x04' + ValueStateValues[value] + b'\xff'
        self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0: 'Auto',
            1: 'Indoor',
            2: 'Outdoor',
            3: 'One Push',
            4: 'ATW',
            5: 'Manual'
        }

        WhiteBalanceCmdString = b'\x81\x09\x04\x35\xff'
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateWhiteBalance')

    def SetZoom(self, value, qualifier):

        SpeedConstraints = {
            'Min': 0,
            'Max': 7
            }

        ValueStateValues = {
            'Tele': 32,
            'Wide': 48
        }
        if SpeedConstraints['Min'] <= qualifier['Speed'] <= SpeedConstraints['Max']:
            if value == 'Stop':
                ZoomCmdString = b'\x81\x01\x04\x07\x00\xff'
            else:
                ZoomCmdString = b'\x81\x01\x04\x07' + pack('>B', ValueStateValues[value] + qualifier['Speed']) + b'\xff'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ErrorStates = {
            1: 'Message Length Error',
            2: 'Syntax Error',
            4: 'Command Canceled',
            5: 'No Socket',
            65: 'Command not Executable',
        }
        if response[2] in ErrorStates and len(response) == 4 and (response[1] >> 4) == 6:
            print('Error from device: {0}'.format(ErrorStates[response[2]]))
            response = b''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xff')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xff')
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
