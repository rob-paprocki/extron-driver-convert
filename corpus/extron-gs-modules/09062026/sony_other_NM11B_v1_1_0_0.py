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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DestinationRoutingStatus': {'Parameters': ['Destination'], 'Status': {}},
            'DestinationStatus': {'Parameters': ['Destination'], 'Status': {}},
            'MatrixRoutingCommand': {'Parameters': ['Source', 'Destination'], 'Status': {}},
            'SourceRoutingStatus': {'Parameters': ['Source', 'Destination'], 'Status': {}},
            'SourceStatus': {'Parameters': ['Source'], 'Status': {}},
            'SystemStatus': {'Status': {}},
        }

        self._NumberofSources = 5 
        self._NumberofDestinations = 5

        self.srcRex = re.compile('S[0-9]{1,2}:(E|D)')
        self.dstRex = re.compile('D[0-9]{1,2}:(E|D)')
        self.xptRex = re.compile('(S[0-9]{1,2}D[0-9]{1,2}):')

        self.Matrix = []

    @property
    def NumberofSources(self):
        return self._NumberofSources

    @NumberofSources.setter
    def NumberofSources(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofSources = value
        else:
            print('Invalid NumberOfSources value, range is from 1 to 15')

        if self._NumberofSources + self._NumberofDestinations:
            print('Combined total of sources and destinations in system exceeds 16.')

    @property
    def NumberofDestinations(self):
        return self._NumberofDestinations

    @NumberofDestinations.setter
    def NumberofDestinations(self, value):
        if 1 <= int(value) <= 15:
            self._NumberofDestinations = value
        else:
            print('Invalid NumberOfSources value, range is from 1 to 15')

        if self._NumberofSources + self._NumberofDestinations:
            print('Combined total of sources and destinations in system exceeds 16.')

    
    def UpdateSourceRoutingStatus(self, value, qualifier) :
        self.UpdateDestinationRoutingStatus(value, qualifier)
            
    def UpdateDestinationRoutingStatus(self, value, qualifier):
        DestinationRoutingStatusCmdString = 'ReadXptMatrix;'
        res = self.__UpdateHelper('DestinationRoutingStatus', DestinationRoutingStatusCmdString, value, qualifier)
        if res:
            try:
                value = re.findall(self.xptRex, res)
                matrix = len(value)
                if matrix == self._NumberofDestinations:
                    for i in range(matrix):
                        destination = value[i][-1]
                        newSource = value[i][-3]
                        try:
                            oldSource = self.Matrix[int(destination)]
                            if oldSource != newSource:
                                self.WriteStatus('DestinationRoutingStatus', newSource, {'Destination': destination})

                                if oldSource:
                                    self.WriteStatus('SourceRoutingStatus', 'Not Routed', {'Source': oldSource, 'Destination': destination})
                                self.WriteStatus('SourceRoutingStatus', 'Routed', {'Source': newSource, 'Destination': destination})
                                self.Matrix[int(destination)] = newSource
                        except(IndexError):
                            self.Error(['Driver Parameters incorrectly configured'])

                elif matrix > 0:
                    for i in range(matrix):
                        value1 = value[i]

                        for j in range(self._NumberofDestinations):
                            oldSource = self.Matrix[j]
                            if 'D' + str(j) not in value1:
                                self.WriteStatus('DestinationRoutingStatus', 'No Source', {'Destination': str(j)})
                                if oldSource:
                                    self.WriteStatus('SourceRoutingStatus', 'Not Routed', {'Source': oldSource, 'Destination': str(j)})
                                self.Matrix[j] = None
                            else:
                                destination = value1[-1]
                                newSource = value1[-3]
                                try:
                                    oldSource = self.Matrix[int(destination)]
                                    if oldSource != newSource:
                                        self.WriteStatus('DestinationRoutingStatus', newSource, {'Destination': destination})

                                        if oldSource:
                                            self.WriteStatus('SourceRoutingStatus', 'Not Routed', {'Source': oldSource, 'Destination': destination})
                                        self.WriteStatus('SourceRoutingStatus', 'Routed', {'Source': newSource, 'Destination': destination})
                                        self.Matrix[int(destination)] = newSource
                                except(IndexError):
                                    self.Error(['Driver Parameters incorrectly configured'])

                else:

                    for dst in range(self._NumberofDestinations):
                        self.WriteStatus('DestinationRoutingStatus', 'No Source', {'Destination': str(dst)})
                        for src in range(self._NumberofSources):
                            self.WriteStatus('SourceRoutingStatus', 'Not Routed', {'Source': str(src), 'Destination': str(dst)})
                    self.Matrix = [None for i in range(self._NumberofDestinations)]

            except (ValueError):
                self.Error(['Destination Routing Status has invalid/unexpected response'])

    def UpdateDestinationStatus(self, value, qualifier):

        ValueStateValues = {
            'E': 'Enabled',
            'D': 'Disabled'
        }

        if 0 <= int(qualifier['Destination']) <= self._NumberofDestinations - 1:
            DestinationStatusCmdString = 'ReadAvIf;'
            res = self.__UpdateHelper('DestinationStatus', DestinationStatusCmdString, value, qualifier)
            if res:
                try:
                    value = re.findall(self.dstRex, res)
                    for i in range(len(value)):
                        self.WriteStatus('DestinationStatus', ValueStateValues[value[i]], {'Destination': str(i)})
                except (KeyError, IndexError, ValueError):
                    self.Error(['Destination Status has invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDestinationStatus')

    def SetMatrixRoutingCommand(self, value, qualifier):

        srcVal = qualifier['Source']
        dstVal = qualifier['Destination']

        if 0 <= int(srcVal) <= self._NumberofSources - 1 and 0 <= int(dstVal) <= self._NumberofDestinations - 1:
            MatrixRoutingCommandCmdString = 'SwitchXpt -x \x7BS' + srcVal + 'D' + dstVal + '\x7D;'
            self.__SetHelper('MatrixRoutingCommand', MatrixRoutingCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixRoutingCommand')

    def UpdateSourceStatus(self, value, qualifier):

        ValueStateValues = {
            'E': 'Enabled',
            'D': 'Disabled'
        }

        if 0 <= int(qualifier['Source']) <= self._NumberofSources - 1:
            SourceStatusCmdString = 'ReadAvIf;'
            res = self.__UpdateHelper('SourceStatus', SourceStatusCmdString, value, qualifier)
            if res:
                try:
                    value = re.findall(self.srcRex, res)
                    for i in range(len(value)):
                        self.WriteStatus('SourceStatus', ValueStateValues[value[i]], {'Source': str(i)})
                except (KeyError, IndexError, ValueError):
                    self.Error(['Source Status has invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateSourceStatus')

    def UpdateSystemStatus(self, value, qualifier):

        ValueStateValues = {
            'R': 'Running',
            'W': 'Warning',
            'E': 'Error',
            'I': 'Initializing',
            'F': 'Finalizing',
            'S': 'Stop'
        }

        SystemStatusCmdString = 'ReadSystem;'
        res = self.__UpdateHelper('SystemStatus', SystemStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[4]]
                self.WriteStatus('SystemStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['System Status has invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'ERROR{COMMAND};': 'Command/parameter error',
            'ERROR{DISCONNECTED};': 'Cannot connect to NSM',
            'ERROR{AUTH};': 'Authentication error in connection to NSM',
            'ERROR;': 'Other error'
        }

        if response in DEVICE_ERROR_CODES:
            errorstring = DEVICE_ERROR_CODES[response]
            self.Error([errorstring])
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b';')
            if not res:
                self.Error(['{0} has invalid/Unexpected Response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b';')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Matrix = [None for i in range(self._NumberofDestinations)]

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
