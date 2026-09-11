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
        self.Models = {}
        self.DeviceID = '01'


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '3DFormat': { 'Status': {}},
            '3DMode': { 'Status': {}},
            '3DSyncInvert': { 'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
            }




    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        #self._DeviceID= value
        if value == 'Broadcast':
            self._DeviceID = '99'
        else:
            self._DeviceID = '{0:02d}'.format(int(value))

    def Set3DFormat(self, value, qualifier):

        States = {
            'Frame Sequential'  : '01370', 
            'Top/ Bottom'       : '01371', 
            'Side By Side'      : '01372', 
            'Frame Packing'     : '01373'
        }


        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('3DFormat', CmdString , value, qualifier)
    def Update3DFormat(self, value, qualifier):

        States = {
            '0' : 'Frame Sequential', 
            '1' : 'Top/ Bottom', 
            '2' : 'Side By Side', 
            '3' : 'Frame Packing'
        }

        CmdString = 'V' + self.DeviceID + 'G0137\r'
        res = self.__UpdateHelper('3DFormat', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('3DFormat',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for 3D Fromat'])

    def Set3DMode(self, value, qualifier):

        States = {
            'Off'       : '01350', 
            'DLP-Link'  : '01351', 
            'IR'        : '01352'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('3DMode', CmdString , value, qualifier)
    def Update3DMode(self, value, qualifier):

        States = {
            '0' : 'Off', 
            '1' : 'DLP-Link', 
            '2' : 'IR'
        }

        CmdString = 'V' + self.DeviceID + 'G0135\r'
        res = self.__UpdateHelper('3DMode', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('3DMode',  States[res[1]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for 3D Mode'])

    def Set3DSyncInvert(self, value, qualifier):

        States = {
            'On'    : '01361', 
            'Off'   : '01360'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('3DSyncInvert', CmdString , value, qualifier)
    def Update3DSyncInvert(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        CmdString = 'V' + self.DeviceID + 'G0136\r'
        res = self.__UpdateHelper('3DSyncInvert', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('3DSyncInvert',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for 3D Sync Invert'])

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Fill'      : '03010', 
            '4:3'       : '03011', 
            '16:9'      : '03012', 
            'Letterbox' : '03013', 
            'Native'    : '03014', 
            '2.35:1'    : '03015'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('AspectRatio', CmdString , value, qualifier)
    def UpdateAspectRatio(self, value, qualifier):

        States = {
            '0' : 'Fill', 
            '1' : '4:3', 
            '2' : '16:9', 
            '3' : 'Letterbox', 
            '4' : 'Native', 
            '5' : '2.35:1'
        }

        CmdString = 'V' + self.DeviceID + 'G0301\r'
        res = self.__UpdateHelper('AspectRatio', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Aspect Ratio'])

    def SetAutoImage(self, value, qualifier):

        CmdString = 'V' + self.DeviceID + 'S0003\r'
        self.__SetHelper('AutoImage', CmdString , value, qualifier)


    def SetDisplayMode(self, value, qualifier):

        States = {
            'Presentation'  : '01080', 
            'Bright'        : '01081', 
            'Game'          : '01082', 
            'Movie'         : '01083', 
            'Vivid'         : '01084', 
            'TV'            : '01085', 
            'sRGB'          : '01086', 
            'DICOM SIM'     : '01088', 
            'User 1'        : '01089', 
            'User 2'        : '01090:'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('DisplayMode', CmdString , value, qualifier)
    def UpdateDisplayMode(self, value, qualifier):

        States = {
            '0' : 'Presentation', 
            '1' : 'Bright', 
            '2' : 'Game', 
            '3' : 'Movie', 
            '4' : 'Vivid', 
            '5' : 'TV', 
            '6' : 'sRGB', 
            '8' : 'DICOM SIM', 
            '9' : 'User 1', 
            '10' : 'User 2'
        }

        CmdString = 'V' + self.DeviceID + 'G0108\r'
        res = self.__UpdateHelper('DisplayMode', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('DisplayMode',  States[res[1:-1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Display Mode'])

    def UpdateFilterUsage(self, value, qualifier):


        CmdString = 'V' + self.DeviceID + 'G0105\r'
        res = self.__UpdateHelper('FilterUsage', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('FilterUsage',  int(res[1:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Filter Usage'])

    def SetFreeze(self, value, qualifier):

        States = {
            'On'    : '03041', 
            'Off'   : '03040'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('Freeze', CmdString , value, qualifier)
    def UpdateFreeze(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        CmdString = 'V' + self.DeviceID + 'G0304\r'
        res = self.__UpdateHelper('Freeze', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Freeze'])

    def SetInput(self, value, qualifier):

        States = {
            'RGB'         : '0201', 
            'DVI'         : '0203', 
            'Video'       : '0204', 
            'BNC'         : '0207', 
            'HDMI 1'      : '0206', 
            'HDMI 2'      : '0209', 
            'HDMI 3/ MHL' : '0212', 
            'HDBaseT'     : '0215'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('Input', CmdString , value, qualifier)
    def UpdateInput(self, value, qualifier):

        States = {
            '1'  : 'RGB', 
            '3'  : 'DVI', 
            '4'  : 'Video', 
            '7'  : 'BNC', 
            '6'  : 'HDMI 1', 
            '9'  : 'HDMI 2', 
            '12' : 'HDMI 3/ MHL', 
            '15' : 'HDBaseT'
        }

        CmdString = 'V' + self.DeviceID + 'G0220\r'
        res = self.__UpdateHelper('Input', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('Input',  States[res[1:-1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Input'])

    def SetLampMode(self, value, qualifier):

        States = {
            'Normal'            : '03190', 
            'Eco'               : '03191', 
            'Eco Plus'          : '03192', 
            'Dimming'           : '03193', 
            'Extreme Dimming'   : '03194', 
            'Custom Light'      : '03195'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('LampMode', CmdString , value, qualifier)
    def UpdateLampMode(self, value, qualifier):

        States = {
            '0' : 'Normal', 
            '1' : 'Eco', 
            '2' : 'Eco Plus', 
            '3' : 'Dimming', 
            '4' : 'Extreme Dimming', 
            '5' : 'Custom Light'
        }

        CmdString = 'V' + self.DeviceID + 'G0139\r'
        res = self.__UpdateHelper('LampMode', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampMode',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Mode'])

    def UpdateLampUsage(self, value, qualifier):

        CmdString = 'V' + self.DeviceID + 'G0004\r'
        res = self.__UpdateHelper('LampUsage', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('LampUsage',  int(res[1:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Lamp Usage'])

    def SetPower(self, value, qualifier):

        States = {
            'On'    : '0001', 
            'Off'   : '0002', 
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('Power', CmdString , value, qualifier)
    def UpdatePower(self, value, qualifier):

        States = {
            '2' : 'On', 
            '1' : 'Off', 
            '3' : 'Cooling Down', 
            '0' : 'Reset'
        }

        CmdString = 'V' + self.DeviceID + 'G0007\r'
        res = self.__UpdateHelper('Power', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('Power',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Power'])

    def SetVideoMute(self, value, qualifier):

        States = {
            'On'  : '03021', 
            'Off' : '03020'
        }

        CmdString = 'V' + self.DeviceID + 'S' + States[value] + '\r'
        self.__SetHelper('VideoMute', CmdString , value, qualifier)
    def UpdateVideoMute(self, value, qualifier):

        States = {
            '1' : 'On', 
            '0' : 'Off'
        }

        CmdString = 'V' + self.DeviceID + 'G0302\r'
        res = self.__UpdateHelper('VideoMute', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute',  States[res[1]] , qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response for Video Mute'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 10:
            CmdString = 'V' + self.DeviceID + 'S' + str(3050 + value) + '\r'
            self.__SetHelper('Volume', '0' + CmdString , value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
    def UpdateVolume(self, value, qualifier):

        CmdString = 'V' + self.DeviceID + 'G0305\r'
        res = self.__UpdateHelper('Volume', CmdString , value, qualifier)
        if res:
            try:
                self.WriteStatus('Volume',  int(res[1:-1]) , qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response for Volume'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        response = response.decode()
        if response == 'F\r':
            self.Error(['Error message received from device'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['Invalid/unexpected response'])
            else:
                res = self.__CheckResponseForErrors(command , res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.DeviceID == '99':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            return self.__CheckResponseForErrors(command , res)
                    
            

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

