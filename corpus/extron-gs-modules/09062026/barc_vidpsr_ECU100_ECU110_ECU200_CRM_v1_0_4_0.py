from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'CloseApplicationWindow': {'Parameters': ['Display', 'Window'], 'Status': {}},
            'Enable': {'Parameters': ['Tiles', 'Perspective'], 'Status': {}},
            'Identify': {'Parameters': ['Perspective'], 'Status': {}},
            'Load': {'Parameters': ['Display', 'Layout'], 'Status': {}},
            'Share': {'Parameters': ['Tiles', 'Displays', 'Perspectives'], 'Status': {}},
            'Show': {'Parameters': ['Tiles', 'Perspectives', 'Sources'], 'Status': {}},
            'Swap': {'Parameters': ['Perspective', 'Tiles'], 'Status': {}},
            'Update': {'Parameters': ['New Value', 'System Variable'], 'Status': {}},
        }


    def FormatQualifier(self, qualifier):
        if '"' in qualifier:
            qualifier = '\"' + qualifier.replace('"', '\\"') + '\"'
            return qualifier
        if ' ' in qualifier or '+' in qualifier:
            qualifier = '\"' + qualifier + '\"'
        return qualifier

    def SetCloseApplicationWindow(self, value, qualifier):

        Window = qualifier['Window']
        Display = self.FormatQualifier(qualifier['Display'])
        CloseCmdString = ''

        if value == 'Close Window':
            if qualifier['Window'] == '' and qualifier['Display'] == '':          # eg: closeWindow
                CloseCmdString = 'closeWindow\r\n'
            elif qualifier['Window'] != '' and qualifier['Display'] == '':          # eg: closeWindow Notepad
                CloseCmdString = 'closeWindow {0}\r\n'.format(Window)
            elif qualifier['Window'] != '' and qualifier['Display'] != '':          # eg: closeWindow Notepad D1
                CloseCmdString = 'closeWindow {0} {1}\r\n'.format(Window, Display)
            else:                                                                   # Discard Others
                self.Discard('Inappropriate Command for SetCloseApplicationWindow')
        elif value == 'Close All Windows':
            if qualifier['Display'] == '':
                CloseCmdString = 'closeAllWindows\r\n'                                # eg: closeAllWindows
            else:
                CloseCmdString = 'closeAllWindows {0}\r\n'.format(Display)            # eg: closeAllWindows D1
        else:
            self.Discard('Inappropriate Command for SetCloseApplicationWindow')

        self.__SetHelper('CloseApplicationWindow', CloseCmdString, value, qualifier)

    def SetEnable(self, value, qualifier):

        if qualifier['Perspective'] == '':
            self.Discard('Inappropriate Command for SetEnable')
        else:
            Perspective = self.FormatQualifier(qualifier['Perspective'])
            Tiles = self.FormatQualifier(qualifier['Tiles'])
            EnableCmdString = ''
            if value == 'Enable' and qualifier['Tiles'] != '':
                EnableCmdString = 'enable {0} {1}\r\n'.format(Perspective, Tiles)
            elif value == 'Enable' and qualifier['Tiles'] == '':
                EnableCmdString = 'enable {0}\r\n'.format(Perspective)

            elif value == 'Disable' and qualifier['Tiles'] != '':
                EnableCmdString = 'disable {0} {1}\r\n'.format(Perspective, Tiles)
            elif value == 'Disable' and qualifier['Tiles'] == '':
                EnableCmdString = 'disable {0}\r\n'.format(Perspective)
            else:
                self.Discard('Inappropriate Command for SetEnable')

            self.__SetHelper('Enable', EnableCmdString, value, qualifier)

    def SetIdentify(self, value, qualifier):

        if qualifier['Perspective'] == '':
            self.Discard('Inappropriate Command for SetIdentify')
        else:
            Perspective = self.FormatQualifier(qualifier['Perspective'])
            IdentifyCmdString = 'identify {0}\r\n'.format(Perspective)
            self.__SetHelper('Identify', IdentifyCmdString, value, qualifier)

    def SetLoad(self, value, qualifier):

        if qualifier['Layout'] == '':
            self.Discard('Inappropriate Command for SetLoad')
        else:
            Layout = self.FormatQualifier(qualifier['Layout'])
            Display = self.FormatQualifier(qualifier['Display'])

            if qualifier['Display'] == '':
                LoadCmdString = 'load {0}\r\n'.format(Layout)                 # eg: load L1
            else:
                LoadCmdString = 'load {0} {1}\r\n'.format(Layout, Display)    # eg: load L1 D1

            self.__SetHelper('Load', LoadCmdString, value, qualifier)

    def SetShare(self, value, qualifier):

        Perspectives = self.FormatQualifier(qualifier['Perspectives'])
        Displays = self.FormatQualifier(qualifier['Displays'])
        Tiles = self.FormatQualifier(qualifier['Tiles'])

        ShareCmdString = ''

        if qualifier['Perspectives'] == '' and value == 'Share':
            self.Discard('Inappropriate Command for SetShare')
        elif qualifier['Perspectives'] != '' and value == 'Share':
            if qualifier['Displays'] == '' and qualifier['Tiles'] == '':             # eg: share P1
                ShareCmdString = 'share {0}\r\n'.format(Perspectives)
            elif qualifier['Displays'] != '' and qualifier['Tiles'] == '':             # eg: share P1 D2
                ShareCmdString = 'share {0} {1}\r\n'.format(Perspectives, Displays)
            elif qualifier['Displays'] != '' and qualifier['Tiles'] != '':             # eg: share P1 D2 3
                ShareCmdString = 'share {0} {1} {2}\r\n'.format(Perspectives, Displays, Tiles)
            else:
                self.Discard('Inappropriate Command for SetShare')
        elif value == 'Unshare':
            if qualifier['Perspectives'] == '' and qualifier['Displays'] == '':    # eg: unshare
                ShareCmdString = 'unshare\r\n'
            elif qualifier['Perspectives'] != '' and qualifier['Displays'] == '':    # eg: unshare P1
                ShareCmdString = 'unshare {0}\r\n'.format(Perspectives)
            elif qualifier['Perspectives'] != '' and qualifier['Displays'] != '':    # eg: unshare P1 D1
                ShareCmdString = 'unshare {0} {1}\r\n'.format(Perspectives, Displays)
            else:
                self.Discard('Inappropriate Command for SetShare')   # Discard Others
        else:
                self.Discard('Inappropriate Command for SetShare')

        self.__SetHelper('Share', ShareCmdString, value, qualifier) 

    def SetShow(self, value, qualifier):

        if qualifier['Sources'] == '' or qualifier['Perspectives'] == '': 
            self.Discard('Inappropriate Command for SetShow')
        else: 
            Sources        = self.FormatQualifier(qualifier['Sources'])
            Perspectives   = self.FormatQualifier(qualifier['Perspectives'])
            Tiles          = self.FormatQualifier(qualifier['Tiles'])

            if qualifier['Tiles'] == '':
                ShowCmdString = 'show {0} {1}\r\n'.format(Sources, Perspectives)                  # eg: show S1 P1
            else:
                ShowCmdString = 'show {0} {1} {2}\r\n'.format(Sources, Perspectives, Tiles)       # eg: show S1 P1 2
        
            self.__SetHelper('Show', ShowCmdString, value, qualifier)

    def SetSwap(self, value, qualifier):

        if qualifier['Tiles'] == '' or qualifier['Perspective'] == '': 
            self.Discard('Inappropriate Command for SetSwap')
        else:
            Tiles = self.FormatQualifier(qualifier['Tiles'])
            Perspective = self.FormatQualifier(qualifier['Perspective'])

            SwapCmdString = 'swap {0} {1}\r\n'.format(Tiles, Perspective)
        
            self.__SetHelper('Swap', SwapCmdString, value, qualifier) 
    def SetUpdate(self, value, qualifier):

        if qualifier['System Variable'] == '' or qualifier['New Value'] == '': 
            self.Discard('Inappropriate Command for SetUpdate') 
        else:
            UpdateCmdString = 'update {0} {1}\r\n'.format(qualifier['System Variable'], qualifier['New Value'])
            self.__SetHelper('Update', UpdateCmdString, value, qualifier) 

    def __CheckResponseForErrors(self, sourceCmdName, response):
        pass

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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