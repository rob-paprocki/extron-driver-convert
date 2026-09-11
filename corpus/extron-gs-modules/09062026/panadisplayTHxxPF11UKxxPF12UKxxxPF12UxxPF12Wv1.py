from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
        self.Models = {
            'TH-42PF11UK': self.pana_other,
            'TH-50PF11UK': self.pana_other,
            'TH-58PF11UK': self.pana_other,
            'TH-65PF11UK': self.pana_other,
            'TH-85PF12UK': self.pana_other,
            'TH-65PF12UK': self.pana_other,
            'TH-85PF12W': self.pana_other,
            'TH-58PF12UK': self.pana_other,
            'TH-103PF12U': self.pana_103,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'InputType': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\x02]QAS:(ZOOM|FULL|JUST|NORM|SELF|SJST|SNOM|SFUL|ZOM2)[\x03]'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'[\x02]QAM:(0|1)[\x03]'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'[\x02]QSP:BTL(MEN|ALL|OFF)[\x03]'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'[\x02]QMI:(SL1|SL2|SL3|PC1|SL1A|SL1B|SL2A|SL2B)[\x03]'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'[\x02]QSU:CMP(RGB|YBR)[\x03]'), self.__MatchInputType, None)
            self.AddMatchString(re.compile(b'[\x02]QSP:OSD(1|0)[\x03]'), self.__MatchOnScreenDisplay, None)
            self.AddMatchString(re.compile(b'[\x02]QSI:(SL1A|SL1B|SL2A|SL2B|SL3|PC1)[\x03]'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'[\x02]QDW:(TWN|POP|PIP|PIN|OFF)[\x03]'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'[\x02]QPW:(0|1)[\x03]'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'[\x02]QVM:(0|1)[\x03]'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'[\x02]QAV:([0-9]{2})[\x03]'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        CmdString = self.AspectStates[value]
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        CmdString = '\x02QAS\x03'
        self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        value = self.ReturnAspectStates[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoImage(self, value, qualifier):

        CmdString = '\x02DGE:ASU1\x03'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '\x02AMT:1\x03',
            'Off': '\x02AMT:0\x03',
            }
        CmdString = States[value]
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        CmdString = '\x02QAM\x03'
        self.__UpdateHelper('AudioMute', CmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        Status = {
            '1': 'On',
            '0': 'Off',
           }
        value = Status[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        States = {
            'Mode 1': '\x02OSP:BTLMEN\x03',
            'Mode 2': '\x02OSP:BTLALL\x03',
            'Off': '\x02OSP:BTLOFF\x03',
            }
        CmdString = States[value]
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        CmdString = '\x02QSP:BTL\x03'
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        Status = {
            'MEN': 'Mode 1',
            'ALL': 'Mode 2',
            'OFF': 'Off',
           }
        value = Status[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        States = {
            'Slot 1': '\x02IMS:SL1\x03',
            'Slot 2': '\x02IMS:SL2\x03',
            'Slot 3': '\x02IMS:SL3\x03',
            'PC': '\x02IMS:PC1\x03',
            'Slot 1 Input A': '\x02IMS:SL1A\x03',
            'Slot 1 Input B': '\x02IMS:SL1B\x03',
            'Slot 2 Input A': '\x02IMS:SL2A\x03',
            'Slot 2 Input B': '\x02IMS:SL2B\x03',
            }
        CmdString = States[value]
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        CmdString = '\x02QMI\x03'
        self.__UpdateHelper('Input', CmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        Status = {
            'SL1': 'Slot 1',
            'SL2': 'Slot 2',
            'SL3': 'Slot 3',
            'PC1': 'PC',
            'SL1A': 'Slot 1 Input A',
            'SL1B': 'Slot 1 Input B',
            'SL2A': 'Slot 2 Input A',
            'SL2B': 'Slot 2 Input B',
        }
        value = Status[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetInputType(self, value, qualifier):

        States = {
            'RGB': '\x02SSU:CMPRGB\x03',
            'Component': '\x02SSU:CMPYBR\x03',
            }
        CmdString = States[value]
        self.__SetHelper('InputType', CmdString, value, qualifier)

    def UpdateInputType(self, value, qualifier):

        CmdString = '\x02QSU:CMP\x03'
        self.__UpdateHelper('InputType', CmdString, value, qualifier)

    def __MatchInputType(self, match, tag):

        Status = {
            'RGB': 'RGB',
            'YBR': 'Component',
        }
        value = Status[match.group(1).decode()]
        self.WriteStatus('InputType', value, None)

    def SetOnScreenDisplay(self, value, qualifier):

        States = {
            'On': '\x02OSP:OSD1\x03',
            'Off': '\x02OSP:OSD0\x03',
            }
        CmdString = States[value]
        self.__SetHelper('OnScreenDisplay', CmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):

        CmdString = '\x02QSP:OSD\x03'
        self.__UpdateHelper('OnScreenDisplay', CmdString, value, qualifier)

    def __MatchOnScreenDisplay(self, match, tag):

        Status = {
            '1': 'On',
            '0': 'Off',
        }
        value = Status[match.group(1).decode()]
        self.WriteStatus('OnScreenDisplay', value, None)

    def SetPIPInput(self, value, qualifier):

        States = {
            'Slot 1 A': '\x02ISS:SL1A\x03',
            'Slot 1 B': '\x02ISS:SL1B\x03',
            'Slot 2 A': '\x02ISS:SL2A\x03',
            'Slot 2 B': '\x02ISS:SL2B\x03',
            'Slot 3': '\x02ISS:SL3\x03',
            'PC': '\x02ISS:PC1\x03',
            }
        CmdString = States[value]
        self.__SetHelper('PIPInput', CmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        CmdString = '\x02QSI\x03'
        self.__UpdateHelper('PIPInput', CmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        Status = {
            'SL1A': 'Slot 1 A',
            'SL1B': 'Slot 1 B',
            'SL2A': 'Slot 2 A',
            'SL2B': 'Slot 2 B',
            'SL3': 'Slot 3',
            'PC1': 'PC',
        }
        value = Status[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPMode(self, value, qualifier):

        States = {
            'Twin Picture': '\x02DWA:TWN\x03',
            'POP': '\x02DWA:POP\x03',
            'PIP': '\x02DWA:PIP\x03',
            'PIN': '\x02DWA:PIN\x03',
            'Off': '\x02DWA:OFF\x03',
            }
        CmdString = States[value]
        self.__SetHelper('PIPMode', CmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        CmdString = '\x02QDW\x03'
        self.__UpdateHelper('PIPMode', CmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        Status = {
            'TWN': 'Twin Picture',
            'POP': 'POP',
            'PIP': 'PIP',
            'PIN': 'PIN',
            'OFF': 'Off',
        }
        value = Status[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPSwap(self, value, qualifier):

        CmdString = '\x02DWA:SWP\x03'
        self.__SetHelper('PIPSwap', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': '\x02PON\x03',
            'Off': '\x02POF\x03',
            }
        CmdString = States[value]
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = '\x02QPW\x03'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        Status = {
            '1': 'On',
            '0': 'Off',
           }
        value = Status[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': '\x02VMT:1\x03',
            'Off': '\x02VMT:0\x03',
            }
        CmdString = States[value]
        self.__SetHelper('VideoMute', CmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        CmdString = '\x02QVM\x03'
        self.__UpdateHelper('VideoMute', CmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        Status = {
            '1': 'On',
            '0': 'Off',
           }
        value = Status[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= int(value) <= 63:
            temp = str(value)
            CmdString = '\x02AVL:' + temp.zfill(2) + '\x03'
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
             print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        CmdString = '\x02QAV\x03'
        self.__UpdateHelper('Volume', CmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def pana_other(self):

        self.AspectStates = {
            'Zoom': '\x02DAM:ZOOM\x03',
            'Full': '\x02DAM:FULL\x03',
            'Just': '\x02DAM:JUST\x03',
            '4:3': '\x02DAM:NORM\x03',
            'Auto': '\x02DAM:SELF\x03',
            'Just-2': '\x02DAM:SJST\x03',
            '4:3-2': '\x02DAM:SNOM\x03',
            'H-Fill': '\x02DAM:SFUL\x03'
        }

        self.ReturnAspectStates = {
            'ZOOM': 'Zoom',
            'FULL': 'Full',
            'JUST': 'Just',
            'NORM': '4:3',
            'SELF': 'Auto',
            'SJST': 'Just-2',
            'SNOM': '4:3-2',
            'SFUL': 'H-Fill'
        }

    def pana_103(self):

        self.AspectStates = {
            'Zoom': '\x02DAM:ZOOM\x03',
            'Full': '\x02DAM:FULL\x03',
            'Just': '\x02DAM:JUST\x03',
            '4:3': '\x02DAM:NORM\x03',
            'Auto': '\x02DAM:SELF\x03',
            'Just-2': '\x02DAM:SJST\x03',
            '4:3-2': '\x02DAM:SNOM\x03',
            'H-Fill': '\x02DAM:SFUL\x03',
            'Zoom 2': '\x02DAM:ZOM2\x03'
        }

        self.ReturnAspectStates = {
            'ZOOM': 'Zoom',
            'FULL': 'Full',
            'JUST': 'Just',
            'NORM': '4:3',
            'SELF': 'Auto',
            'SJST': 'Just-2',
            'SNOM': '4:3-2',
            'SFUL': 'H-Fill',
            'ZOM2': 'Zoom 2'
        }

            
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
