from extronlib.interface import EthernetClientInterface
class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Enumerate'         : {'Parameters':['MAC Address'], 'Status': {}},
            'Reboot'            : {'Parameters':['MAC Address'], 'Status': {}},
            'RefreshInfo'       : {'Parameters':['MAC Address'], 'Status': {}},
            'RefreshSettings'   : {'Parameters':['MAC Address'], 'Status': {}},
            'RollCall'          : {'Parameters':['MAC Address'], 'Status': {}},
            'Sequence'          : {'Parameters':['MAC Address'], 'Status': {}},
            'SwitchOutlet'      : {'Parameters':['MAC Address','Outlet ID'], 'Status': {}},
            }

    def SetEnumerate(self, value, qualifier):

        MAC = qualifier['MAC Address']
        EnumerateCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command\><enumerate/></command></device>'.format(MAC)
        self.__SetHelper('Enumerate', EnumerateCmdString, value, qualifier)

    def SetReboot(self, value, qualifier):

        MAC = qualifier['MAC Address']
        RebootCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><reboot/></command></device>'.format(MAC)
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRefreshInfo(self, value, qualifier):

        MAC = qualifier['MAC Address']
        RefreshInfoCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><refreshinfo/></command></device>'.format(MAC)
        self.__SetHelper('RefreshInfo', RefreshInfoCmdString, value, qualifier)

    def SetRefreshSettings(self, value, qualifier):

        MAC = qualifier['MAC Address']
        RefreshSettingsCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><refreshsettings/></command></device>'.format(MAC)
        self.__SetHelper('RefreshSettings', RefreshSettingsCmdString, value, qualifier)

    def SetRollCall(self, value, qualifier):

        MAC = qualifier['MAC Address']
        RollCallCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><rollcall/></command></device>'.format(MAC)
        self.__SetHelper('RollCall', RollCallCmdString, value, qualifier)

    def SetSequence(self, value, qualifier):

        MAC = qualifier['MAC Address']
        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        SequenceCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><sequence>{1}</sequence></command></device>'.format(MAC, ValueStateValues[value])
        self.__SetHelper('Sequence', SequenceCmdString, value, qualifier)

    def SetSwitchOutlet(self, value, qualifier):

        MAC = qualifier['MAC Address']
        Outlet = qualifier['Outlet ID']

        OutletConstraints = {
                'Min' : 1,
                'Max' : 3
                }

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }
        
        if OutletConstraints['Min'] <= int(Outlet) <= OutletConstraints['Max']:
            SwitchOutletCmdString = '<?xml version="1.0"?><device class="bb232"id="{0}"><command><outlet id=\"{1}\">{2}</outlet></command></device>'.format(MAC, Outlet, ValueStateValues[value])
            self.__SetHelper('SwitchOutlet', SwitchOutletCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSwitchOutlet')

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
