from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'CloseAllWindows': { 'Status': {}},
            'CloseWindow': {'Parameters': ['Window ID'], 'Status': {}},
            'Input': {'Parameters': ['Window ID', 'Provider', 'Date Time'], 'Status': {}},
            'Layout': {'Parameters': ['Action'], 'Status': {}},
            'WindowPosition': {'Parameters': ['Window ID', 'Top', 'Left', 'Width', 'Height'], 'Status': {}},
        }
        
    def SetCloseAllWindows(self, value, qualifier):

        CloseAllWindowsCmdString = 'wcmd -closewindows\r\n'
        self.__SetHelper('CloseAllWindows', CloseAllWindowsCmdString, value, qualifier)

    def SetCloseWindow(self, value, qualifier):

        winID = str(qualifier['Window ID'])
        if winID:
            CloseWindowCmdString = 'wcmd -id={0} -closewindow\r\n'.format(winID)
            self.__SetHelper('CloseWindow', CloseWindowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCloseWindow')

    def SetInput(self, value, qualifier):

        winID = str(qualifier['Window ID'])
        provider = qualifier['Provider']
        if winID and provider and value:
            InputCmdString = 'wcmd -id={0} -provider={1} -input={2}\r\n'.format(winID, provider, value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetLayout(self, value, qualifier):

        ActionStates = {
            'Load': 'layout',
            'Save': 'savelayout',
        }

        if value and qualifier['Action'] in ['Load', 'Save', 'Schedule']:
            if qualifier['Action'] == 'Schedule':
                DateTime = qualifier['Date Time'] # Fomat is DD/MM/YYYY HH:MM:SS
                if DateTime:
                    if ' ' in value:
                        LayoutCmdString = 'wcmd -layout="{0}" -scheduled="{1}"\r\n'.format(value, DateTime)
                    else:
                        LayoutCmdString = 'wcmd -layout={0} -scheduled="{1}"\r\n'.format(value, DateTime)
                    self.__SetHelper('Layout', LayoutCmdString, value, qualifier)
            else:
                if ' ' in value:
                    LayoutCmdString = 'wcmd -{0}="{1}"\r\n'.format(ActionStates[qualifier['Action']], value)
                else:
                    LayoutCmdString = 'wcmd -{0}={1}\r\n'.format(ActionStates[qualifier['Action']], value)
                self.__SetHelper('Layout', LayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayout')

    def SetWindowPosition(self, value, qualifier):

        winID = str(qualifier['Window ID'])
        top = str(qualifier['Top'])
        left = str(qualifier['Left'])
        width = str(qualifier['Width'])
        height = str(qualifier['Height'])
        if winID and top and left and width and height:
            WindowPositionCmdString = 'wcmd -id={0} -window={1},{2},{3},{4}\r\n'.format(winID, top, left, width, height)
            self.__SetHelper('WindowPosition', WindowPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPosition')
        
    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

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