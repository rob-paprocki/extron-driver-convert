from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AddScene': {'Parameters': ['Merge Scene Name', 'Scene Name'], 'Status': {}},
            'AutorunControls': {'Status': {}},
            'BatchExecuteCommands': {'Status': {}},
            'CreateMergeScene': {'Parameters': ['Merge Scene Name'], 'Status': {}},
            'DeleteScene': {'Parameters': ['Merge Scene Name', 'Scene Name'], 'Status': {}},
            'HideShowWindow': {'Parameters': ['Window Number'], 'Status': {}},
            'PurgeMergeScene': {'Parameters': ['Merge Scene Name'], 'Status': {}},
            'RecallBySceneName': {'Parameters': ['Scene Name'], 'Status': {}},
            'RecallSceneStep': {'Status': {}},
            'Source': {'Parameters': ['Window Number', 'Input Source Name'], 'Status': {}},
            'SourceInScene': {'Parameters':['Window Number','Input Source Name','Scene Name'], 'Status': {}},
            'WindowPriority': {'Parameters': ['Scene Name', 'Window Number', 'Layer'], 'Status': {}},
            'WindowSizePosition': {'Parameters': ['Horizontal Position', 'Vertical Position', 'Horizontal Size', 'Vertical Size'], 'Status': {}},
            'ZoomPan': {'Parameters': ['Zoom', 'Pan Vertical', 'Pan Horizontal'], 'Status': {}}
        }


    def SetAddScene(self, value, qualifier):

        MergeSceneName = qualifier['Merge Scene Name']
        SceneName = qualifier['Scene Name']
        if SceneName and MergeSceneName:
            CommandString = b'\x01R' + str.encode(MergeSceneName) + b',,' + str.encode(str(SceneName)) + b',1\x0251\x17\x03'
            self.__SetHelper('AddScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAddScene')

    def SetAutorunControls(self, value, qualifier):

        Controls = {
            'Begin from 1st scene': b'0=',
            'Begin from current scene': b'0>',
            'Stop': b'0<',
            'Increment': b'0+',
            'Decrement': b'0-'
        }

        CommandString = b'\x01R\x02' + Controls[value] + b'\x17\x03'
        self.__SetHelper('AutorunControls', CommandString, value, qualifier)

    def SetBatchExecuteCommands(self, value, qualifier):

        BatchCommands = {
            'Begin': b'\x01R\x0241\x17\x03',
            'Execute': b'\x01R\x0242\x17\x03'
        }

        self.__SetHelper('BatchExecuteCommands', BatchCommands[value], value, qualifier)

    def SetCreateMergeScene(self, value, qualifier):

        MergeSceneName = qualifier['Merge Scene Name']

        if MergeSceneName:
            CommandString = b'\x01R' + str.encode(MergeSceneName) + b',,,1\x0251\x17\x03'
            self.__SetHelper('CreateMergeScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCreateMergeScene')

    def SetDeleteScene(self, value, qualifier):

        MergeSceneName = qualifier['Merge Scene Name']
        SceneName = qualifier['Scene Name']
        if SceneName and MergeSceneName:
            CommandString = b'\x01R' + str.encode(MergeSceneName) + b',' + str.encode(SceneName) + b',,1\x0251\x17\x03'
            self.__SetHelper('DeleteScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeleteScene')

    def SetHideShowWindow(self, value, qualifier):

        WindowNumber = qualifier['Window Number']

        Visibility = {
            'Hide': b'0',
            'Show': b'1'
        }

        WindowNumberRange = {
            'Min': 1,
            'Max': 999
        }

        OperationValue = Visibility[value]

        if WindowNumberRange['Min'] <= WindowNumber <= WindowNumberRange['Max']:
            WindowNumber = str(WindowNumber - 1).zfill(4)
            CommandString = b'\x01R' + str.encode(str(WindowNumber)) + OperationValue + b'\x0233\x17\x03'
            self.__SetHelper('HideShowWindow', CommandString, value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def SetPurgeMergeScene(self, value, qualifier):

        MergeSceneName = qualifier['Merge Scene Name']

        if MergeSceneName:
            RemoveCommandString = b'\x01R\x0256\x17\x03'
            RefreshCommandString = b'\x01R' + str.encode(MergeSceneName) + b',,,1\x0251\x17\x03'
            self.__SetHelper('PurgeMergeScene', RemoveCommandString, value, qualifier)
            self.__SetHelper('PurgeMergeScene', RefreshCommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPurgeMergeScene')

    def SetRecallBySceneName(self, value, qualifier):

        sceneName = qualifier['Scene Name']

        if sceneName:
            CommandString = b'\x01\x52' + str.encode(sceneName) + b'\x0207\x17\x03'
            self.__SetHelper('RecallBySceneName', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallBySceneName')

    def SetRecallSceneStep(self, value, qualifier):

        RecallSceneControls = {
            'Next': b'0n',
            'Previous': b'0p'
        }

        CommandString = b'\x01R\x02' + RecallSceneControls[value] + b'\x17\x03'
        self.__SetHelper('RecallSceneStep', CommandString, value, qualifier)

    def SetSource(self, value, qualifier):

        WindowNumberRange = {
            'Min': 1,
            'Max': 999
        }

        WindowNumber = qualifier['Window Number']
        sourceName = qualifier['Input Source Name']

        if sourceName and WindowNumberRange['Min'] <= WindowNumber <= WindowNumberRange['Max']:
            WindowNumber = str(WindowNumber - 1).zfill(4)
            CommandString = b'\x01R' + str.encode(str(WindowNumber)) + str.encode(sourceName) + b'\x0236\x17\x03'
            self.__SetHelper('Source', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSource')

    def SetSourceInScene(self, value, qualifier):
        WindowNumberRange = {
                              'Min': 1,
                              'Max': 999
                            }

        WindowNumber = qualifier['Window Number']
        sourceName = qualifier['Input Source Name']
        SceneName = qualifier['Scene Name']

        if sourceName and SceneName and WindowNumberRange['Min'] <= WindowNumber <= WindowNumberRange['Max']:
            WindowNumber = str(WindowNumber - 1).zfill(4)
            CommandString = b'\x01R'+ str.encode(SceneName) + b',' + str.encode(str(WindowNumber)) + b',' + str.encode(sourceName) + b'\x0252\x17\x03'
            self.__SetHelper('SourceInScene', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SourceInScene')

    def SetWindowPriority(self, value, qualifier):

        Position = {
            'Forward': b'1',
            'Backward': b'0'
        }

        LayerRange = {
            'Min': 0,
            'Max': 999
        }

        WindowNumberRange = {
            'Min': 1,
            'Max': 999
        }

        OperationValue = Position[value]
        WindowNumber = qualifier['Window Number']
        SceneName = qualifier['Scene Name']
        LayerNumber = qualifier['Layer']

        if LayerRange['Min'] <= LayerNumber <= LayerRange['Max']:
            if WindowNumberRange['Min'] <= WindowNumber <= WindowNumberRange['Max']:
                WindowNumber = str(WindowNumber - 1).zfill(4)
                CommandString = b'\x01R' + str.encode(SceneName) + b',' + str.encode(str(WindowNumber)) + b',' + str.encode(str(LayerNumber)) + b',' + OperationValue + b'\x0279\x17\x03'
                self.__SetHelper('WindowPriority', CommandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetWindowPriority')
        else:
            self.Discard('Invalid Command for SetWindowPriority')

    def SetWindowSizePosition(self, value, qualifier):

        HorizontalSize = qualifier['Horizontal Size']
        HorizontalPosition = qualifier['Horizontal Position']
        VerticalSize = qualifier['Vertical Size']
        VerticalPosition = qualifier['Vertical Position']

        PositionRange = {
            'Min': -9999,
            'Max': 99999
        }

        SizeRange = {
            'Min': 0,
            'Max': 99999
        }

        WindowNumberRange = {
            'Min': 1,
            'Max': 999
        }

        if (PositionRange['Min'] <= HorizontalPosition <= PositionRange['Max']) and (PositionRange['Min'] <= VerticalPosition <= PositionRange['Max']):
            if (SizeRange['Min'] <= HorizontalSize <= SizeRange['Max']) and (SizeRange['Min'] <= VerticalSize <= SizeRange['Max']):
                if WindowNumberRange['Min'] <= value <= WindowNumberRange['Max']:
                    value = str(value - 1).zfill(4)
                    HorizontalPosition = str(HorizontalPosition).zfill(5)
                    VerticalPosition = str(VerticalPosition).zfill(5)
                    HorizontalSize = str(HorizontalSize).zfill(5)
                    VerticalSize = str(VerticalSize).zfill(5)
                    CommandString = b'\x01R' + str.encode(str(value)) + str.encode(str(HorizontalPosition)) + str.encode(str(VerticalPosition)) + str.encode(str(HorizontalSize)) + str.encode(str(VerticalSize)) + b'\x0235\x17\x03'
                    self.__SetHelper('WindowSizePosition', CommandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetWindowSizePosition')
            else:
                self.Discard('Invalid Command for SetWindowSizePosition')
        else:
            self.Discard('Invalid Command for SetWindowSizePosition')

    def SetZoomPan(self, value, qualifier):

        Zoom = qualifier['Zoom']
        PanVertical = qualifier['Pan Vertical']
        PanHorizontal = qualifier['Pan Horizontal']

        ZoomConstraints = {
            'Min': 0,
            'Max': 999
        }

        PanConstraints = {
            'Min': 0,
            'Max': 999
        }

        valueConstraints = {
            'Min': 1,
            'Max': 999
        }

        if ZoomConstraints['Min'] <= Zoom <= ZoomConstraints['Max']:
            if (PanConstraints['Min'] <= PanVertical <= PanConstraints['Max']) and (PanConstraints['Min'] <= PanHorizontal <= PanConstraints['Max']):
                if valueConstraints['Min'] <= value <= valueConstraints['Max']:
                    Zoom = str(Zoom).zfill(3)
                    PanVertical = str(PanVertical).zfill(3)
                    PanHorizontal = str(PanHorizontal).zfill(3)
                    value = str(value - 1).zfill(4)
                    CommandString = b'\x01R' + str.encode(str(value)) + str.encode(str(Zoom)) + str.encode(str(PanHorizontal)) + str.encode(str(PanVertical)) + b'\x0234\x17\x03'
                    self.__SetHelper('ZoomPan', CommandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetZoomPan')
            else:
                self.Discard('Invalid Command for SetZoomPan')
        else:
            self.Discard('Invalid Command for SetZoomPan')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
