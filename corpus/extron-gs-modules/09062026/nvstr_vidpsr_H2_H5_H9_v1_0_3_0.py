from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Brightness': {'Parameters': ['Device ID', 'Screen ID'], 'Status': {}},
            'FadeToBlack': {'Parameters': ['Device ID', 'Screen ID'], 'Status': {}},
            'Freeze': {'Parameters':['Device ID','Screen ID'], 'Status': {}},
            'LayerInput': {'Parameters': ['Device ID', 'Screen ID', 'Layer ID', 'Input ID', 'Interface Type', 'Crop ID'], 'Status': {}},
            'LayerPositionandSize': {'Parameters':['Device ID','Screen ID','Layer ID','Width','Height','X','Y'], 'Status': {}},
            'Preset': {'Parameters': ['Device ID', 'Screen ID'], 'Status': {}},
            'PresetSave': {'Parameters':['Device ID','Screen ID','Name','Overwrite'], 'Status': {}},
            'ScreenBKG': {'Parameters':['Device ID','Screen ID','BKG ID'], 'Status': {}},
            'ScreenColor': {'Parameters':['Device ID','Screen ID','Temperature','Eyecare Mode','Image Quality'], 'Status': {}},
        }

    def SetBrightness(self, value, qualifier):

        device_id = qualifier['Device ID']
        screen_id = qualifier['Screen ID']

        if 0 <= device_id and 0 <= screen_id and 0 <= value <= 100:
            BrightnessCmdString = '[{{"cmd":"W0410","deviceId":{},"screenId":{},"brightness":{}}}]'.format(device_id, screen_id, value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetFadeToBlack(self, value, qualifier):

        device_id = qualifier['Device ID']
        screen_id = qualifier['Screen ID']

        ValueStateValues = {
            'On':   0,
            'Off':  1
        }

        if 0 <= device_id and 0 <= screen_id and value in ValueStateValues:
            FadeToBlackCmdString = '[{{"cmd":"W0409","deviceId":{},"screenId":{},"type":{}}}]'.format(device_id, screen_id, ValueStateValues[value])
            self.__SetHelper('FadeToBlack', FadeToBlackCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFadeToBlack')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if 0 <= qualifier['Device ID'] and 0 <= qualifier['Screen ID'] and value in ValueStateValues:
            FreezeCmdString = ''.join(['[{"cmd":"W041A","deviceId":', str(qualifier['Device ID']),
                                        ',"screenId":', str(qualifier['Screen ID']),
                                        ',"enable":', ValueStateValues[value], '}]'])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetLayerInput(self, value, qualifier):

        device_id = qualifier['Device ID']
        screen_id = qualifier['Screen ID']
        layer_id = qualifier['Layer ID']
        input_id = qualifier['Input ID']
        interface_type = qualifier['Interface Type']
        crop_id = qualifier['Crop ID']

        if 0 <= device_id and 0 <= screen_id and 0 <= layer_id and 0 <= input_id and 1 <= interface_type and 0 <= crop_id:
            LayerInputCmdString = '[{{"cmd":"W0506","deviceId":{},"screenId":{},"layerId":{},"inputId":{},"interfaceType":{},"cropId":{}}}]'.format(device_id, screen_id, layer_id, input_id, interface_type, crop_id)
            self.__SetHelper('LayerInput', LayerInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayerInput')

    def SetLayerPositionandSize(self, value, qualifier):

        if (0 <= qualifier['Device ID'] and 0 <= qualifier['Screen ID'] and 0 <= qualifier['Layer ID'] and 0 <= qualifier['Width'] and
            0 <= qualifier['Height'] and 0 <= qualifier['X'] and 0 <= qualifier['Y']):
            LayerPositionandSizeCmdString = ''.join(['[{"cmd":"W0505","screenId":', str(qualifier['Screen ID']),
                                                     ',"deviceId":', str(qualifier['Device ID']),
                                                     ',"layerId":', str(qualifier['Layer ID']),
                                                     ',"width":', str(qualifier['Width']),
                                                     ',"height":', str(qualifier['Height']),
                                                     ',"x":', str(qualifier['X']),
                                                     ',"y":', str(qualifier['Y']), '}]'])
            self.__SetHelper('LayerPositionandSize', LayerPositionandSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayerPositionandSize')

    def SetPreset(self, value, qualifier):

        device_id = qualifier['Device ID']
        screen_id = qualifier['Screen ID']

        if 0 <= device_id and 0 <= screen_id and 0 <= value <= 1999:
            PresetCmdString = '[{{"cmd":"W0605","deviceId":{},"screenId":{},"presetId":{}}}]'.format(device_id, screen_id, value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetPresetSave(self, value, qualifier):

        OverwriteStates = {
            'Yes': '1',
            'No':  '0'
            }

        if 0 <= qualifier['Device ID'] and 0 <= qualifier['Screen ID'] and qualifier['Overwrite'] in OverwriteStates and 0 <= value <= 1999:
            PresetSaveCmdString = ''.join(['[{"cmd":"W0602","screenId":', str(qualifier['Screen ID']),
                                                     ',"deviceId":', str(qualifier['Device ID']),
                                                     ',"presetId":', str(value),
                                                     ',"name":', str(qualifier['Name']),
                                                     ',"overWrite":', OverwriteStates[qualifier['Overwrite']],
                                                     '}]'])
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetScreenBKG(self, value, qualifier):

        ValueStateValues = {
            'On':  '1',
            'Off': '0'
            }

        if 0 <= qualifier['Device ID'] and 0 <= qualifier['Screen ID'] and 0 <= qualifier['BKG ID'] <= 100 and value in ValueStateValues:
            ScreenBKGCmdString = ''.join(['[{"cmd":"W040B","screenId":', str(qualifier['Screen ID']),
                                                     ',"deviceId":', str(qualifier['Device ID']),
                                                     ',"enable":', ValueStateValues[value],
                                                     ',"bkgId":', str(qualifier['BKG ID']),
                                                     '}]'])
            self.__SetHelper('ScreenBKG', ScreenBKGCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenBKG')

    def SetScreenColor(self, value, qualifier):

        EyecareModeStates = {
            'On':  '1',
            'Off': '0'
            }

        ImageQualityStates = {
            'Standard': '0',
            'Document': '1',
            'Conference': '2',
            'Video': '3'
            }

        if (0 <= qualifier['Device ID'] and 0 <= qualifier['Screen ID'] and 2000 <= qualifier['Temperature'] <= 10000 
            and qualifier['Eyecare Mode'] in EyecareModeStates and qualifier['Image Quality'] in ImageQualityStates
            and 0 <= value <= 100):
            ScreenColorCmdString = ''.join(['[{"cmd":"W040E","deviceId":', str(qualifier['Device ID']),
                                            ',"screenId":', str(qualifier['Screen ID']),
                                            ',"imageQualityMode":', ImageQualityStates[qualifier['Image Quality']],
                                            ',"eyeCare":', EyecareModeStates[qualifier['Eyecare Mode']],
                                            ',"contrast":{"all":', str(value), ',"R":', str(value), ',"G":', str(value), ',"B":', str(value),
                                            '},"brightness":{"all":', str(value), ',"R":', str(value), ',"G":', str(value), ',"B":', str(value),
                                            '},"hue":', str(value), ',"saturation":', str(value), ',"colorTemperature":', str(qualifier['Temperature']),
                                            '}]'])
            self.__SetHelper('ScreenColor', ScreenColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenColor')

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