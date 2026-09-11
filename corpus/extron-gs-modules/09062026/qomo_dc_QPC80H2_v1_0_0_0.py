from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Brightness': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'ImageRecall': {'Status': {}},
            'ImageSave': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Record': {'Status': {}},
            'Scroll': {'Status': {}},
            'Source': {'Status': {}},
            'Volume': {'Status': {}},
        }


    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x02\x14\x2E\x54',
            'Down': '\x48\x02\x14\x2F\x54'
        }

        BrightnessCmdString = ValueStateValues[value]
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto': '\x48\x02\x14\x22\x54',
            'Near': '\x48\x02\x14\x23\x54',
            'Far': '\x48\x02\x14\x24\x54'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = '\x48\x02\x14\x15\x54'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetImageRecall(self, value, qualifier):

        ImageRecallCmdString = '\x48\x02\x14\x13\x54'
        self.__SetHelper('ImageRecall', ImageRecallCmdString, value, qualifier)

    def SetImageSave(self, value, qualifier):

        ImageSaveCmdString = '\x48\x02\x14\x12\x54'
        self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x02\x14\x04\x54',
            'Down': '\x48\x02\x14\x05\x54',
            'Left': '\x48\x02\x14\x02\x54',
            'Right': '\x48\x02\x14\x03\x54',
            'Enter': '\x48\x02\x14\x06\x54'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x48\x02\x14\x10\x54',
            'Off': '\x48\x02\x14\x11\x54'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Start': '\x48\x02\x14\x32\x54',
            'Stop': '\x48\x02\x14\x33\x54'
        }

        RecordCmdString = ValueStateValues[value]
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def SetScroll(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x02\x14\x30\x54',
            'Down': '\x48\x02\x14\x31\x54',
            'Stop': '\x48\x02\x14\x37\x54'
        }

        ScrollCmdString = ValueStateValues[value]
        self.__SetHelper('Scroll', ScrollCmdString, value, qualifier)

    def SetSource(self, value, qualifier):

        SourceCmdString = '\x48\x02\x14\x25\x54'
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x02\x14\x28\x54',
            'Down': '\x48\x02\x14\x29\x54'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
# END AUTO GENERATION OF COMMAND DEF  
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
