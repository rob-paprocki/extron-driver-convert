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
        self.Debug = False
        self._DeviceID= '01'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': {'Status': {}},
            '3DInvert': {'Status': {}},
            '3DMode': {'Status': {}},
            '3Dto2D': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioInput': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
            }

    @property
    def DeviceID(self):
        return self._ProjectorID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID= '00'
        elif 1 <= int(value) <= 99:
            self._DeviceID= (value).zfill(2)

    def Set3DFormat(self, value, qualifier):

        States = {
            'Auto'             : '405 0\r', 
            'SBS'              : '405 1\r', 
            'Top and Bottom'   : '405 2\r', 
            'Frame Sequential' : '405 3\r',
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('3DFormat', CmdString, value, qualifier)


    def Set3DInvert(self, value, qualifier):

        States = {
            'On'  : '231 0\r', 
            'Off' : '231 1\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('3DInvert', CmdString, value, qualifier)


    def Set3DMode(self, value, qualifier):

        States = {
            'DLP-Link' : '230 1\r', 
            'IR'       : '230 3\r', 
            'Off'      : '230 0\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('3DMode', CmdString, value, qualifier)


    def Set3Dto2D(self, value, qualifier):

        States = {
            '3D'    : '400 0\r', 
            'Left'  : '400 1\r', 
            'Right' : '400 2\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('3Dto2D', CmdString, value, qualifier)


    def SetAspectRatio(self, value, qualifier):


        States = {
            '4:3'       : '60 1\r', 
            '16:9'      : '60 2\r',
            '16:10'     : '60 3\r',
            'Native'    : '60 6\r',
            'Auto'      : '60 7\r' 
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        States = {
            '1' : '4:3', 
            '2' : '16:9',
            '3' : '16:10',  
            '6' : 'Native', 
            '7' : 'Auto',
            '0' : 'No Aspect Ratio'
        }

        CmdString = '~{0}127 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  States[res[-2]] , qualifier)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioInput(self, value, qualifier):

        States = {
            'Default' : '89 0\r', 
            'Audio 1' : '89 1\r', 
            'Audio 2' : '89 3\r', 
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('AudioInput', CmdString, value, qualifier)


    def SetAudioMute(self, value, qualifier):

        States = {
            'On'  : '03 1\r', 
            'Off' : '03 0\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)


    def SetAutoImage(self, value, qualifier):

        CmdString = '~{0}01 1\r'.format(self._DeviceID)
        self.__SetHelper('AutoImage', CmdString, value, qualifier)


    def SetAVMute(self, value, qualifier):

        States = {
            'On'  : '02 1\r', 
            'Off' : '02 0\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('AVMute', CmdString, value, qualifier)


    def SetClosedCaption(self, value, qualifier):

        States = {
            'Off' : '88 0\r', 
            '1'   : '88 1\r', 
            '2'   : '88 2\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('ClosedCaption', CmdString, value, qualifier)


    def SetDisplayMode(self, value, qualifier):

        States = {
            'Presentation' : '20 1\r', 
            'Bright'       : '20 2\r', 
            'Cinema'       : '20 3\r', 
            'sRGB'         : '20 4\r', 
            'DICOM SIM'    : '20 13\r', 
            'User'         : '20 5\r', 
            '3D'           : '20 9\r',
            'Game'         : '20 12\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('DisplayMode', CmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'On'  : '103 1\r', 
            'Off' : '103 0\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)


    def SetFreeze(self, value, qualifier):

        States = {
            'On'  : '04 1\r', 
            'Off' : '04 0\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('Freeze', CmdString, value, qualifier)


    def SetInput(self, value, qualifier):

        States = {
            'HDMI 1' : '12 1\r', 
            'HDMI 2' : '12 15\r', 
            'VGA 1'  : '12 5\r', 
            'VGA 2'  : '12 6\r',
            'Video'  : '12 10\r',
            'S-Video': '12 10\r',
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('Input', CmdString, value, qualifier)


    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up'    : '140 10\r', 
            'Down'  : '140 14\r', 
            'Left'  : '140 11\r', 
            'Right' : '140 13\r', 
            'Enter' : '140 12\r', 
            'Menu'  : '140 20\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)


    def SetVolume(self, value, qualifier):

        States = {
            'Up'   : '140 18\r', 
            'Down' : '140 17\r'
        }

        CmdString = '~{0}{1}'.format(self._DeviceID, States[value])
        self.__SetHelper('Volume', CmdString, value, qualifier)


    def SetPower(self, value, qualifier):


        States = {
            'On'    : '00 1\r', 
            'Off'   : '00 0\r', 
        }

        CmdString = '~{0}{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)
    def UpdatePower(self, value, qualifier):

        PowerStates = {
            '1' : 'On', 
            '0' : 'Off'
        }

        InputStates = {
            2  :   'VGA 1',
            3  :   'VGA 2',
            4  :   'S-Video',
            5  :   'Video',
            7  :   'HDMI 1',
            8  :   'HDMI 2',
            0  :   'No Input',
        }

        DisplayStates = {
            1  :   'Presentation',
            2  :   'Bright',
            3  :   'Cinema',
            4  :   'sRGB',
            5  :   'User',
            9  :   '3D',
            10 :   'DICOM SIM',
            12 :   'Game',
            0  :   'No Display Mode',
        }

        PowerCmdString = '~{0}150 1\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:


            try:
                self.WriteStatus('Power',  PowerStates[res[2]] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePower')


            try:
                self.WriteStatus('LampUsage',  int(res[3:8]) , qualifier)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePower')


            try:
                self.WriteStatus('Input',  InputStates[int(res[8:10])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePower')


            try:
                self.WriteStatus('DisplayMode',  DisplayStates[int(res[14:16])] , qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdatePower')


    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True' or int(self._DeviceID) == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or int(self._DeviceID) == 0:
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())            

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
