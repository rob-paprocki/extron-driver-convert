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
        self.Models = {
            'DB-VWC2-M4-FR3K': self.dbrd_29_3634_3K,
            'DB-VWC2-M4-FR4K': self.dbrd_29_3634_4K,
            'DB-VWC2-M4-FR6K': self.dbrd_29_3634_6K,
            'DB-VWC2-M4-FR8K': self.dbrd_29_3634_8K,
            'DB-VWC2-M4-FR14K': self.dbrd_29_3634_14K,
            'DB-VWC2-M4-FR26K': self.dbrd_29_3634_26K,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CloseAllWindows': {'Parameters': ['Video Wall ID'], 'Status': {}},
            'CloseWindow': {'Parameters': ['Window ID', 'Video Wall ID'], 'Status': {}},
            'DeleteScene': {'Parameters': ['Video Wall ID'], 'Status': {}},
            'InputSwitching': {'Parameters': ['Window ID', 'Video Wall ID'], 'Status': {}},
            'LayerWindow': {'Parameters': ['Window ID', 'Layer Order', 'Video Wall ID'], 'Status': {}},
            'MoveWindow': {'Parameters': ['Window ID', 'Input Channel', 'Upper Left Coordinate X0', 'Upper Left Coordinate Y0', 'Bottom Right Coordinate X1', 'Bottom Right Coordinate Y1', 'Video Wall ID'], 'Status': {}},
            'OpenWindow': {'Parameters': ['Window ID', 'Input Channel', 'Upper Left Coordinate X0', 'Upper Left Coordinate Y0', 'Bottom Right Coordinate X1', 'Bottom Right Coordinate Y1', 'Video Wall ID'], 'Status': {}},
            'RecallScene': {'Parameters': ['Video Wall ID'], 'Status': {}},
            'RenameScene': {'Parameters': ['Name', 'Video Wall ID'], 'Status': {}},
            'ResizeWindow': {'Parameters': ['Window ID', 'Input Channel', 'Upper Left Coordinate X0', 'Upper Left Coordinate Y0', 'Bottom Right Coordinate X1', 'Bottom Right Coordinate Y1', 'Video Wall ID'], 'Status': {}},
            'SaveScene': {'Parameters': ['Video Wall ID'], 'Status': {}},
            'ScrollingText': {'Parameters': ['Video Wall ID'], 'Status': {}},
            'VideoWallStatus': {'Parameters': ['Video Wall ID'], 'Status': {}},
        }

    def SetCloseAllWindows(self, value, qualifier):

        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4:
            CloseAllWindowsCmdString = '<sall,{0}>'.format(VidWallID)
            self.__SetHelper('CloseAllWindows', CloseAllWindowsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCloseAllWindows')

    def SetCloseWindow(self, value, qualifier):

        winID = qualifier['Window ID']
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= int(VidWallID) <= 4:
            CloseWindowCmdString = '<shut,{0},{1}>'.format(winID, VidWallID)
            self.__SetHelper('CloseWindow', CloseWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCloseWindow')

    def SetDeleteScene(self, value, qualifier):

        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4 and 1 <= int(value) <= 32:
            DeleteSceneCmdString = '<SDEL,{0},{1}>'.format(value, VidWallID)
            self.__SetHelper('DeleteScene', DeleteSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeleteScene')

    def SetInputSwitching(self, value, qualifier):

        winID = qualifier['Window ID']
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= int(VidWallID) <= 4 and 1 <= int(value) <= self.MaxInput:
            InputSwitchingCmdString = '<SWCH,{0},0,{1},{2}>'.format(value, winID, VidWallID)
            self.__SetHelper('InputSwitching', InputSwitchingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSwitching')

    def SetLayerWindow(self, value, qualifier):

        winID = qualifier['Window ID']
        layerOrd = qualifier['Layer Order']
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= layerOrd <= 65535 and 1 <= int(VidWallID) <= 4:
            LayerWindowCmdString = '<movz,{0},{1},{2}>'.format(winID, layerOrd, VidWallID)
            self.__SetHelper('LayerWindow', LayerWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayerWindow')

    def SetMoveWindow(self, value, qualifier):

        winID = int(qualifier['Window ID'])
        channel = qualifier['Input Channel']
        x0 = int(qualifier['Upper Left Coordinate X0'])
        y0 = int(qualifier['Upper Left Coordinate Y0'])
        x1 = int(qualifier['Bottom Right Coordinate X1'])
        y1 = int(qualifier['Bottom Right Coordinate Y1'])
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= int(channel) <= self.MaxInput and 0 <= x0 <= x1 <= 19200  and 0 <= y0 <= y1 <= 19200 and 1 <= int(VidWallID) <= 4:
            MoveWindowCmdString = '<move,{0},{1},0,{2},{3},{4},{5},{6}>'.format(winID, channel, x0, y0, x1, y1, VidWallID)
            self.__SetHelper('MoveWindow', MoveWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMoveWindow. X0 and Y0 Coordinate cannot be smaller than X1 and Y1')

    def SetOpenWindow(self, value, qualifier):

        winID = int(qualifier['Window ID'])
        channel = qualifier['Input Channel']
        x0 = int(qualifier['Upper Left Coordinate X0'])
        y0 = int(qualifier['Upper Left Coordinate Y0'])
        x1 = int(qualifier['Bottom Right Coordinate X1'])
        y1 = int(qualifier['Bottom Right Coordinate Y1'])
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= int(channel) <= self.MaxInput and 0 <= x0 <= x1 <= 19200  and 0 <= y0 <= y1 <= 19200 and 1 <= int(VidWallID) <= 4:
            OpenWindowCmdString = '<open,{0},{1},0,{2},{3},{4},{5},{6}>'.format(winID, channel, x0, y0, x1, y1, VidWallID)
            self.__SetHelper('OpenWindow', OpenWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpenWindow. X0 and Y0 Coordinate cannot be smaller than X1 and Y1')

    def SetRecallScene(self, value, qualifier):

        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4 and 1 <= int(value) <= 32:
            RecallSceneCmdString = '<call,{0},{1}>'.format(value, VidWallID)
            self.__SetHelper('RecallScene', RecallSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallScene')

    def SetRenameScene(self, value, qualifier):

        name = qualifier['Name']
        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4 and 1 <= int(value) <= 32:
            RenameSceneCmdString = '<SREN,{0},{1},{2}>'.format(value, name, VidWallID)
            self.__SetHelper('RenameScene', RenameSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRenameScene')

    def SetResizeWindow(self, value, qualifier):

        winID = qualifier['Window ID']
        channel = qualifier['Input Channel']
        x0 = int(qualifier['Upper Left Coordinate X0'])
        y0 = int(qualifier['Upper Left Coordinate Y0'])
        x1 = int(qualifier['Bottom Right Coordinate X1'])
        y1 = int(qualifier['Bottom Right Coordinate Y1'])
        VidWallID = qualifier['Video Wall ID']
        if 1 <= winID <= 65535 and 1 <= int(channel) <= self.MaxInput and 0 <= x0 <= x1 <= 19200  and 0 <= y0 <= y1 <= 19200 and 1 <= int(VidWallID) <= 4:
            ResizeWindowCmdString = '<size,{0},{1},0,{2},{3},{4},{5},{6}>'.format(winID, channel, x0, y0, x1, y1, VidWallID)
            self.__SetHelper('ResizeWindow', ResizeWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResizeWindow. X0 and Y0 Coordinate cannot be smaller than X1 and Y1')

    def SetSaveScene(self, value, qualifier):

        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4 and 1 <= int(value) <= 32:
            SaveSceneCmdString = '<save,{0},{1}>'.format(value, VidWallID)
            self.__SetHelper('SaveScene', SaveSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSaveScene')

    def SetScrollingText(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'SRSD',
            'Disable': 'ERSD'
        }

        VidWallID = qualifier['Video Wall ID']
        if 1 <= int(VidWallID) <= 4:
            ScrollingTextCmdString = '<{0},{1}>'.format(ValueStateValues[value], VidWallID)
            self.__SetHelper('ScrollingText', ScrollingTextCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScrollingText')

    def UpdateVideoWallStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Disabled'
        }

        CmdString = '<RCNG>'
        res = self.__UpdateHelper('VideoWallStatus', CmdString, value, qualifier)
        if res:
            try:
                values = res.split(',')
                for i in range(1, len(values)):
                    value = ValueStateValues[values[i][0]]
                    self.WriteStatus('VideoWallStatus', value, {'Video Wall ID': str(i)})
            except (ValueError, IndexError, KeyError):
                self.Error(['Video Wall Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERR' in response:
            self.Error(['{0} is not supported'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'>')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'>')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def dbrd_29_3634_3K(self):
        self.MaxInput = 24

    def dbrd_29_3634_4K(self):
        self.MaxInput = 32

    def dbrd_29_3634_6K(self):
        self.MaxInput = 56

    def dbrd_29_3634_8K(self):
        self.MaxInput = 60

    def dbrd_29_3634_14K(self):
        self.MaxInput = 84

    def dbrd_29_3634_26K(self):
        self.MaxInput = 168
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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
