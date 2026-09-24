from Extron2.BaseDriver import BaseDriver
import time
from struct import pack


class _1bynd_19_4743(BaseDriver):
    """1bynd_19_4743

    Created on  03/23/2020 10:42:08

    
    Supported Models:
        PTZ-IP12
        PTZ-IP20

    DRIVER STYLE       
        Synchronous due to ambiguous command responses  

    COMMAND STRUCTURE
        COMMAND DELIMITER:  '\xFF'
        COMMAND EXAMPLE:    '\x81\x01\x04\x00\x02\xFF'  (Power On, Camera ID 1)
        RESPONSE EXAMPLE:   '\x90\x50\x02\xFF'          (Power is On, Camera ID 1)

    COMMAND NOTES
        Manufacturer confirmed ethernet control uses UDP port 5500 and commands are same as RS232.

        SetHelper:  A minimum query delay is used in the driver, because set commands respond with an ACK and
                    completion/error. See 1 Beyond PTZ-IP12-IP20 Manual.pdf,  page 22.
                    \xFF delitag in UpdateHelper can catch completion/error when spamming commands without a
                    query delay which causes statuses to flip. Referenced sony_19_4539_v1_0_1.pkp.


    ------------------------------------------------------------------
    DERIVED DRIVER - Crestron 1 Beyond IV-CAM-i12 / i20

    Derived by experiments/skeleton_i20/build_i20.py from Extron's own
    1bynd_19_4743 (PTZ-IP12/IP20) package. Extron's original code is
    unchanged except where noted as [PATCH].

    The i20 command bytes were resolved from Crestron's SchemaVersion 2.0
    driver definition (Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg), not from
    a generic VISCA reference. Cross-vendor agreement was verified on the
    commands both vendors implement - identical bytes AND identical value
    tables (e.g. exposure mode Full Auto=0x00, Manual=0x03, Shutter
    Priority=0x0A, Iris Priority=0x0B).

    NOT YET RUN AGAINST AN I20. Every added command is a transcription of
    Crestron's declarative spec. The package has run on an IPCP Pro 360 with a
    PC playing the camera, so the requests have been observed on a wire, but
    no reply has come from a real camera. Treat status feedback in particular
    as provisional: the reply rules are Crestron's where their driver declares
    one, and the documentation's or VISCA's convention where it does not.
    ------------------------------------------------------------------

    REVISION HISTORY
    Version         Date            Notes
    1_0_1           6/14/2021       Changed ethernet to TCP based on testing. No script changes. DR# 62249

    1_0_0           3/23/2020       Initial version. DR# 59047, 59048.
    """

################################################################
# INITIALIZATION
################################################################
    def __init__(self, configs):
        """Driver Constructor
        Read/set information passed in via configuration data.

        """
        super().__init__(configs)

        self.Commands = {
            'AutoExposure':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'AutoFocus':            {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Backlight':            {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Focus':                {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Speed'],                    'Status': {}},
            'Gain':                 {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'Iris':                 {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'PanTilt':              {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Pan Speed', 'Tilt Speed'],  'Status': {}},
            'Power':                {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Preset':               {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Action'],                   'Status': {}},
            'Shutter':              {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'UserDefinedCommand':   {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'UserDefinedString':    {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,                                               'Status': {}},
            'WhiteBalance':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Zoom':                 {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Speed'],                    'Status': {}},
            # [PATCH E3] i20 command set. Bytes resolved from Crestron's
            # SchemaVersion 2.0 definition by resolve_visca.py.
            'TrackingFraming':      {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'TrackingMode':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'ZoomPosition':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,   'Parameters': ['Speed'],                    'Status': {}},
            'PanTiltAngle':         {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Pan Speed', 'Tilt Speed', 'Pan', 'Tilt'],   'Status': {}},
            'PanAngleStatus':       {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                              'Status': {}},
            'TiltAngleStatus':      {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                              'Status': {}},
            'PanTiltHome':          {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'FreezeFrame':          {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Menu':                 {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'Identify':             {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'TrackingProfile':      {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'PresetZone':           {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'TrackingShot':         {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'IndicatorLight':       {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,   'Parameters': ['Color', 'Brightness'],      'Status': {}},
            'CameraOutput':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'IntelligentSwitching': {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'CameraConnectionStatus': {'Set': False, 'Update': True,    'Live': True,   'Emulated': False,  'Parameters': ['Camera'],                   'Status': {}},
            'Reboot':               {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            # [PATCH E7] Parity with Crestron's I20 driver (v1.6).
            'ExposureCompensationMode': {'Set': True, 'Update': True,   'Live': True,   'Emulated': True,                                               'Status': {}},
            'ExposureCompensation': {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'FocusPosition':        {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'OnePushAutoFocus':     {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'AutoFocusBehavior':    {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'AutoFocusSensitivity': {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'AutoPrivacyMode':      {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'AutoSoftwareUpdate':   {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'DeviceModel':          {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                                              'Status': {}},
            'RomVersion':           {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                                              'Status': {}},
            'PanSpeedMaxStatus':    {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                                              'Status': {}},
            'TiltSpeedMaxStatus':   {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                                              'Status': {}}
        }

        initError = [] 

        try:
            self.Unidirectional = configs['Unidirectional']
            if self.Unidirectional not in ['True', 'False']:
                initError.append('Unidirectional set to an invalid value: {0}'.format(configs['Unidirectional']))
        except KeyError:
            initError.append('Missing Unidirectional Parameter.')

        try:
            self.DeviceID = configs['DriverParams']['Device ID']

            if 1 <= int(self.DeviceID) <= 7:
                self.DeviceID = 0x80 + int(self.DeviceID)
            else:
                initError.append('Invalid Device ID Parameter.')
        except KeyError:
            initError.append('Missing Device ID Parameter.')
        except (ValueError, TypeError):
            initError.append('Device ID Parameter is the wrong type.')

        try:
            self.CommandPacing = configs['CommandPacing']
            if not 0 <= self.CommandPacing <= 30:
                initError.append('CommandPacing must be greater than or equal to 0 and less than or equal to 30')
        except KeyError:
            initError.append('Missing CommandPacing Parameter.')
        except TypeError:
            initError.append('CommandPacing Parameter is the wrong type.')
                    
        try:
            self.DefaultResponseTimeout = configs['ResponseTimeout']
            if self.DefaultResponseTimeout <= 0:
                initError.append('ResponseTimeout must be greater than 0.')
        except KeyError:
            initError.append('Missing ResponseTimeout Parameter.')
        except TypeError:
            initError.append('ResponseTimeout Parameter is the wrong type.')
                        
        if initError:
            self.Error(initError)
            self.Disable()

################################################################
### BEGIN AUTO GENERATION OF COMMAND DEF
################################################################

    # Begin AutoExposure
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetAutoExposure(self, value, qualifier):
        """Set Auto Exposure
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority':    0x0B,
            'Bright':           0x0D
        }

        if value in ValueStateValues:
            AutoExposureCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('AutoExposure'):
                self.WriteAutoExposure(value, qualifier, 'Emulated')
                self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    # 1 Beyond PTZ-IP12-IP20 Manual, page 26
    def _cmd_UpdateAutoExposure(self, value, qualifier):
        """Update Auto Exposure
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteAutoExposure(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def WriteAutoExposure(self, value, qualifier, context):
        """Write Auto Exposure
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('AutoExposure', value, qualifier, context)

    def ReadAutoExposure(self, qualifier, context):
        """Read Auto Exposure
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('AutoExposure', qualifier, context)

    # Begin AutoFocus
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 23
    def _cmd_SetAutoFocus(self, value, qualifier):
        """Set Auto Focus
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('AutoFocus'):
                self.WriteAutoFocus(value, qualifier, 'Emulated')
                self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # 1 Beyond PTZ-IP12-IP20 Manual, page 26
    def _cmd_UpdateAutoFocus(self, value, qualifier):
        """Update Auto Focus
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        AutoFocusCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteAutoFocus(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def WriteAutoFocus(self, value, qualifier, context):
        """Write Auto Focus
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('AutoFocus', value, qualifier, context)

    def ReadAutoFocus(self, qualifier, context):
        """Read Auto Focus
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('AutoFocus', qualifier, context)

    # Begin Backlight
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetBacklight(self, value, qualifier):
        """Set Backlight
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('Backlight'):
                self.WriteBacklight(value, qualifier, 'Emulated')
                self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    # 1 Beyond PTZ-IP12-IP20 Manual, page 26
    def _cmd_UpdateBacklight(self, value, qualifier):
        """Update Backlight
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteBacklight(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def WriteBacklight(self, value, qualifier, context):
        """Write Backlight
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('Backlight', value, qualifier, context)

    def ReadBacklight(self, qualifier, context):
        """Read Backlight
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('Backlight', qualifier, context)

    # Begin Focus
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 23
    def _cmd_SetFocus(self, value, qualifier):
        """Set Focus
        value: Enum
        qualifier: {'Speed' : Decimal}
        """
        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        speed = int(qualifier['Speed'])

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)
            if self.__SafeToSet('Focus'):
                self.__SetHelper('Focus', FocusCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin Gain
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetGain(self, value, qualifier):
        """Set Gain
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            GainCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('Gain'):
                self.__SetHelper('Gain', GainCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin Iris
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetIris(self, value, qualifier):
        """Set Iris
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            IrisCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('Iris'):
                self.__SetHelper('Iris', IrisCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin PanTilt
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 25
    def _cmd_SetPanTilt(self, value, qualifier):
        """Set Pan Tilt
        value: Enum
        qualifier: {'Pan Speed' : Decimal, 'Tilt Speed' : Decimal}
        """
        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303,
            'Home':         0x04,
            'Reset':        0x05
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = pack('>5B', self.DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', self.DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)

            if self.__SafeToSet('PanTilt'):
                self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin Power
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 23
    def _cmd_SetPower(self, value, qualifier):
        """Set Power
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('Power'):
                self.WritePower(value, qualifier, 'Emulated')
                self.__SetHelper('Power', PowerCmdString, value, qualifier, 5)
        else:
            self.Discard('Invalid Command')

    # 1 Beyond PTZ-IP12-IP20 Manual, page 26
    def _cmd_UpdatePower(self, value, qualifier):
        """Update Power
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off',
            0x04: 'Internal Power Circuit Error'
        }

        PowerCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WritePower(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def WritePower(self, value, qualifier, context):
        """Write Power
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('Power', value, qualifier, context)

    def ReadPower(self, qualifier, context):
        """Read Power
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('Power', qualifier, context)

    # Begin Preset
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetPreset(self, value, qualifier):
        """Set Preset
        value: Decimal
        qualifier: {'Action' : Enum}
        """
        ActionStates = {
            'Reset':    0x00,
            'Save':     0x01,
            'Recall':   0x02
        }

        action = qualifier['Action']

        if action in ActionStates and 0 <= value <= 255:
            PresetCmdString = pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, ActionStates[action], value, 0xFF)
            if self.__SafeToSet('Preset'):
                self.__SetHelper('Preset', PresetCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin Shutter
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 24
    def _cmd_SetShutter(self, value, qualifier):
        """Set Shutter
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            ShutterCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            if self.__SafeToSet('Shutter'):
                self.__SetHelper('Shutter', ShutterCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin UserDefinedCommand
    ####################################################################################################################
    #
    def _cmd_SetUserDefinedCommand(self, value, qualifier):
        cmdstring = self.ReadUserDefinedString(qualifier, 'Emulated')
        if cmdstring:
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('UserDefinedCommand', cmdstring, None, None)

    # Begin UserDefinedString
    ####################################################################################################################
    #
    def _cmd_SetUserDefinedString(self, value, qualifier):
        """Set User Defined String
        value: String
        qualifier: None
        """
        self.WriteUserDefinedString(value, qualifier, 'Emulated')

    def WriteUserDefinedString(self, value, qualifier, context):
        """Write User Defined String
        value: String
        qualifier: None

        """
        self.WriteStatusHelper('UserDefinedString', value, qualifier, context)

    def ReadUserDefinedString(self, qualifier, context):
        """Read User Defined String
        value: String
        qualifier: None

        """
        return self.ReadStatusHelper('UserDefinedString', qualifier, context)

    # Begin WhiteBalance
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 23
    def _cmd_SetWhiteBalance(self, value, qualifier):
        """Set White Balance
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'Auto':             0x00,
            'Indoor':           0x01,
            'Outdoor':          0x02,
            'One Push':         0x03,
            'Manual':           0x05,
            'One Push Trigger': ''
        }

        if value in ValueStateValues:
            if value != 'One Push Trigger':
                WhiteBalanceCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF)
            else:
                WhiteBalanceCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x10, 0x05, 0xFF)

            if self.__SafeToSet('WhiteBalance'):
                if value != 'One Push Trigger':
                    self.WriteWhiteBalance(value, qualifier, 'Emulated')
                self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    # 1 Beyond PTZ-IP12-IP20 Manual, page 26
    def _cmd_UpdateWhiteBalance(self, value, qualifier):
        """Update White Balance
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x00: 'Auto',
            0x01: 'Indoor',
            0x02: 'Outdoor',
            0x03: 'One Push',
            0x05: 'Manual'
        }

        WhiteBalanceCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteWhiteBalance(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def WriteWhiteBalance(self, value, qualifier, context):
        """Write White Balance
        value: Enum
        qualifier: None

        """
        self.WriteStatusHelper('WhiteBalance', value, qualifier, context)

    def ReadWhiteBalance(self, qualifier, context):
        """Read White Balance
        value: Enum
        qualifier: None

        """
        return self.ReadStatusHelper('WhiteBalance', qualifier, context)

    # Begin Zoom
    ####################################################################################################################
    # 1 Beyond PTZ-IP12-IP20 Manual, page 23
    def _cmd_SetZoom(self, value, qualifier):
        """Set Zoom
        value: Enum
        qualifier: {'Speed' : Decimal}
        """
        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            # [PATCH E2] Extron's shipped driver transmits ValueStateValues[value] here,
            # discarding the speed computed immediately above, so zoom always ran at
            # speed 0. Crestron encodes this as one {SpeedAndDirection} byte; `speed`
            # already holds exactly that.
            ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)
            if self.__SafeToSet('Zoom'):
                self.__SetHelper('Zoom', ZoomCmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

################################################################

################################################################
### [PATCH E4] i20 COMMAND SET
###
### Byte sequences resolved from Crestron's SchemaVersion 2.0 driver
### definition for IV-CAM-I20_IP. See experiments/skeleton_i20/i20_wire_table.txt.
################################################################

    def _Nibbles(self, value, count):
        """Split an integer into `count` bytes, each carrying one nibble in
        its low 4 bits, most-significant first.

        This is Crestron's ViscaAssemble4LowerNibbles / ViscaAssemble2LowerNibbles,
        which finding 07 identified as having no declarative definition in their
        driver - the behaviour lived only as compiled IL. It is standard VISCA
        absolute-position encoding, so it is reimplemented here rather than
        recovered: 0x1A2B -> [0x01, 0x0A, 0x02, 0x0B].
        """
        return [(int(value) >> (4 * (count - 1 - i))) & 0x0F for i in range(count)]

    def _FromNibbles(self, data):
        """Inverse of _Nibbles (Crestron's ViscaExtractNibbles)."""
        out = 0
        for b in data:
            out = (out << 4) | (b & 0x0F)
        return out

    def _Signed16(self, value):
        """Read a 16-bit position the way SetPanTiltAngle writes it (pan & 0xFFFF),
        so a negative angle reads back as itself. The documentation gives the
        nibble layout but not the sign convention; the camera's is unmeasured."""
        return value - 0x10000 if value & 0x8000 else value

    def _PresetOpcode(self, preset):
        """Recall a reserved preset. The i20 exposes its auto-switching and
        framing features this way rather than through dedicated opcodes."""
        return pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x02, preset, 0xFF)

    # Some replies carry more than one status: pan and tilt, the camera output
    # and the switching flag, the model and the ROM version, the two maximum
    # speeds. GC polls every bound status separately, so without this each
    # would send the same inquiry. Extron's pana_19_5702 queries at most once
    # per window and writes every status the reply carries; this does the same.
    #
    # The window is deliberately shorter than any poll interval. The updates
    # in one polling pass arrive milliseconds apart, so later ones reuse the
    # first reply; the next pass is seconds away, so no pass is swallowed. A
    # query that got no reply caches nothing and is retried. The cache is a
    # class attribute rather than an __init__ line, to keep this patch
    # additive; each instance creates its own on first use.
    INQUIRY_WINDOW = 1.0
    _inquiryCache = None

    def _SharedInquiry(self, command, cmdString, value, qualifier, parse):
        """Send cmdString at most once per window; parse() writes the statuses."""
        if self._inquiryCache is None:
            self._inquiryCache = {}
        now = time.monotonic()
        hit = self._inquiryCache.get(cmdString)
        if hit is not None and now - hit[0] < self.INQUIRY_WINDOW:
            return hit[1]
        res = self.__UpdateHelper(command, cmdString, value, qualifier)
        if not res:
            return None
        try:
            parsed = parse(res, qualifier)
        except (KeyError, IndexError):
            self.Error(['%s: Invalid/unexpected response' % command])
            return None
        self._inquiryCache[cmdString] = (now, parsed)
        return parsed

    # Begin TrackingFraming
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: StartTrackingFraming / StopTrackingFraming
    def _cmd_SetTrackingFraming(self, value, qualifier):
        """Set Tracking Framing
        value: Enum ('Start'/'Stop')
        qualifier: None
        """
        ValueStateValues = {
            'Start':    0x50,
            'Stop':     0x51,
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            if self.__SafeToSet('TrackingFraming'):
                self.WriteTrackingFraming(value, qualifier, 'Emulated')
                self.__SetHelper('TrackingFraming', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetTrackingFraming -> 81 09 08 01 FF
    #
    # Reply layout is documented (reference/crestron-visca/COMMANDS.md, the
    # CAM_TrackingInq rows):
    #     y0 50 02 FF   tracking active
    #     y0 50 03 FF   tracking paused
    # which is VISCA's usual 0x02=on / 0x03=off convention, the same one Power
    # and IR_ReceiveInq use on this camera.
    def _cmd_UpdateTrackingFraming(self, value, qualifier):
        """Update Tracking Framing
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'Start',
            0x03: 'Stop'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x08, 0x01, 0xFF)
        res = self.__UpdateHelper('TrackingFraming', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteTrackingFraming(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['TrackingFraming: Invalid/unexpected response'])

    def WriteTrackingFraming(self, value, qualifier, context):
        self.WriteStatusHelper('TrackingFraming', value, qualifier, context)

    def ReadTrackingFraming(self, qualifier, context):
        return self.ReadStatusHelper('TrackingFraming', qualifier, context)

    # Begin TrackingMode
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: EnableGroupTracking     -> reserved preset 0x52
    #                         EnablePresenterTracking -> reserved preset 0x53
    #
    # These were two commands until 20027, one value each, so GC could switch
    # either ON and neither OFF - a latching button with no release, and an
    # emulated status that could never go back. They are one setting on the
    # camera: Crestron's Presenter Tracking Settings page describes Group Track
    # as a toggle, "when disabled, the camera only tracks one presenter at a
    # time". So one command with two values, which is what the hardware has.
    #
    # !! DOCS AND IMPLEMENTATION DISAGREE ON 0x53 !!
    # Crestron's own driver names preset 0x53 "EnablePresenterTracking".
    # Crestron's own documentation (COMMANDS.md section 10, from the
    # Reserved-Presets page) names preset 83 decimal - the same byte -
    # "Pause Group Tracking". Five of the six reserved presets agree exactly
    # between the two sources (0x50, 0x51, 0x52, 0x5F, 0x63); this is the
    # only one that does not.
    #
    # The value names here are deliberately the one reading BOTH sources
    # support: 0x52 selects group framing, 0x53 selects single-presenter
    # framing - whether you reach it by "enabling presenter tracking" or by
    # "pausing group tracking". So merging does not decide the open question.
    # Step 7 of PROTOCOL.md still settles it on hardware: start group tracking
    # with 0x52, then send 0x53, and observe whether group tracking PAUSES
    # (documentation is right) or presenter mode ENGAGES (driver is right).
    def _cmd_SetTrackingMode(self, value, qualifier):
        """Set Tracking Mode
        value: Enum ('Group'/'Presenter')
        qualifier: None
        """
        ValueStateValues = {
            'Group':     0x52,
            'Presenter': 0x53
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            if self.__SafeToSet('TrackingMode'):
                self.WriteTrackingMode(value, qualifier, 'Emulated')
                self.__SetHelper('TrackingMode', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetGroupTracking -> 81 C2 09 06 FF
    #   reply  y0 50 00 0v FF    v 01 group tracking active, 00 not
    # Crestron's ViscaGroupTrackingStatusInquiryResponse reads that one byte
    # through MapBooleanToBinaryOnOff and derives presenter tracking as its
    # inverse (InvertBoolean): one flag, the same two values this command sets.
    # Live from 20028; until then this status was only ever what was last sent.
    def _cmd_UpdateTrackingMode(self, value, qualifier):
        """Update Tracking Mode
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x01: 'Group',
            0x00: 'Presenter'
        }

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x06, 0xFF)
        res = self.__UpdateHelper('TrackingMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteTrackingMode(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['TrackingMode: Invalid/unexpected response'])

    def WriteTrackingMode(self, value, qualifier, context):
        self.WriteStatusHelper('TrackingMode', value, qualifier, context)

    def ReadTrackingMode(self, qualifier, context):
        return self.ReadStatusHelper('TrackingMode', qualifier, context)

    # Begin ZoomPosition
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetZoomPosition
    #   81 01 04 47 {ZoomSpeedHex} {Y4} {Y3} {Y2} {Y1} FF
    # Note the speed byte: standard VISCA CAM_Zoom Direct has no such field.
    # It is a 1 Beyond extension, and is taken from Crestron's template.
    def _cmd_SetZoomPosition(self, value, qualifier):
        """Set Zoom Position
        value: Decimal (0 - 16384)
        qualifier: {'Speed' : Decimal}
        """
        try:
            speed = int(qualifier['Speed'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if 0 <= int(value) <= 16384 and 0 <= speed <= 7:
            cmdString = pack('>10B', self.DeviceID, 0x01, 0x04, 0x47, speed,
                             *(self._Nibbles(value, 4) + [0xFF]))
            if self.__SafeToSet('ZoomPosition'):
                self.WriteZoomPosition(value, qualifier, 'Emulated')
                self.__SetHelper('ZoomPosition', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetZoomPosition -> 81 09 04 47 FF
    def _cmd_UpdateZoomPosition(self, value, qualifier):
        """Update Zoom Position
        value: Decimal
        qualifier: {'Speed' : Decimal}
        """
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x47, 0xFF)
        res = self.__UpdateHelper('ZoomPosition', cmdString, value, qualifier)
        if res:
            try:
                # Reply 90 50 0p 0q 0r 0s FF - four nibbles, as sent.
                value = self._FromNibbles(res[2:6])
                self.WriteZoomPosition(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['ZoomPosition: Invalid/unexpected response'])

    def WriteZoomPosition(self, value, qualifier, context):
        self.WriteStatusHelper('ZoomPosition', value, qualifier, context)

    def ReadZoomPosition(self, qualifier, context):
        return self.ReadStatusHelper('ZoomPosition', qualifier, context)

    # Begin PanTiltAngle
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetPanTiltAngle
    #   81 01 06 02 {PanSpeed} {TiltSpeed} {Y4..Y1} {Z4..Z1} FF
    def _cmd_SetPanTiltAngle(self, value, qualifier):
        """Set Pan/Tilt Angle
        value: None
        qualifier: {'Pan Speed': Decimal, 'Tilt Speed': Decimal,
                    'Pan': Decimal, 'Tilt': Decimal}

        Every parameter arrives in the qualifier because none of them is the
        asset's `Value`. That is Extron's own convention for a multi-number
        command - see pana_19_5702's PanTiltAbsolutePosition, whose asset is
        `Pan(Decimal) | Tilt(Decimal)` with no Value and whose script reads
        `qualifier['Pan']`. An earlier revision took pan and tilt from `value`
        as a dict, which GC cannot express and which therefore never ran.
        """
        try:
            panSpeed = int(qualifier['Pan Speed'])
            tiltSpeed = int(qualifier['Tilt Speed'])
            pan = int(qualifier['Pan'])
            tilt = int(qualifier['Tilt'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if 1 <= panSpeed <= 0x18 and 1 <= tiltSpeed <= 0x14:
            payload = ([panSpeed, tiltSpeed]
                       + self._Nibbles(pan & 0xFFFF, 4)
                       + self._Nibbles(tilt & 0xFFFF, 4)
                       + [0xFF])
            cmdString = pack('>15B', self.DeviceID, 0x01, 0x06, 0x02, *payload)
            if self.__SafeToSet('PanTiltAngle'):
                self.__SetHelper('PanTiltAngle', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Position feedback is split in two because ONE VISCA inquiry returns both
    # numbers and a GC command can only carry one Value. Extron solves it the
    # same way in pana_19_5702 (PanPositionStatus / TiltPositionStatus), so the
    # split is their pattern rather than our invention.
    #
    # Extron also solves the COST of that split, and this follows them. In
    # pana_19_5702, _cmd_UpdatePanPositionStatus queries at most once every
    # three seconds and writes every position the reply carries, so a bound Pan
    # and a bound Tilt cost one query between them instead of two. Measured on
    # 20026 before this change: two identical 81 09 06 12 FF per poll cycle,
    # the second reply used for its tilt half alone. _SharedInquiry below is
    # that pattern, and from 20028 three more pairs use it.
    #
    # Crestron IV-CAM-I20_IP: GetPanTiltAngle -> 81 09 06 12 FF
    #   reply  y0 50 0p0q0r0s 0t0u0v0w FF
    def _PanTiltAngleInquiry(self, command, value, qualifier):
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x12, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParsePanTiltAngle)

    def _ParsePanTiltAngle(self, res, qualifier):
        pos = (self._Signed16(self._FromNibbles(res[2:6])),
               self._Signed16(self._FromNibbles(res[6:10])))
        self.WritePanAngleStatus(pos[0], qualifier, 'Live')
        self.WriteTiltAngleStatus(pos[1], qualifier, 'Live')
        return pos

    def _cmd_UpdatePanAngleStatus(self, value, qualifier):
        """Update Pan Angle Status
        value: Decimal
        qualifier: None
        """
        self._PanTiltAngleInquiry('PanAngleStatus', value, qualifier)

    def WritePanAngleStatus(self, value, qualifier, context):
        self.WriteStatusHelper('PanAngleStatus', value, qualifier, context)

    def ReadPanAngleStatus(self, qualifier, context):
        return self.ReadStatusHelper('PanAngleStatus', qualifier, context)

    def _cmd_UpdateTiltAngleStatus(self, value, qualifier):
        """Update Tilt Angle Status
        value: Decimal
        qualifier: None
        """
        self._PanTiltAngleInquiry('TiltAngleStatus', value, qualifier)

    def WriteTiltAngleStatus(self, value, qualifier, context):
        self.WriteStatusHelper('TiltAngleStatus', value, qualifier, context)

    def ReadTiltAngleStatus(self, qualifier, context):
        return self.ReadStatusHelper('TiltAngleStatus', qualifier, context)

    # Begin PanTiltHome
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: PanTiltReset -> 81 01 06 05 FF
    def _cmd_SetPanTiltHome(self, value, qualifier):
        """Set Pan/Tilt Home
        value: Enum ('Reset')
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0x01, 0x06, 0x05, 0xFF)
        if self.__SafeToSet('PanTiltHome'):
            self.__SetHelper('PanTiltHome', cmdString, value, qualifier, 3)

    # Begin FreezeFrame
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetFreezeFrame -> 81 01 04 62 {OnOff} FF
    # OnOff from Crestron's MapBooleanToViscaOnOff: On=0x02, Off=0x03.
    def _cmd_SetFreezeFrame(self, value, qualifier):
        """Set Freeze Frame
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x62,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('FreezeFrame'):
                self.WriteFreezeFrame(value, qualifier, 'Emulated')
                self.__SetHelper('FreezeFrame', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetFreezeFrame -> 81 09 04 62 FF
    def _cmd_UpdateFreezeFrame(self, value, qualifier):
        """Update Freeze Frame
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('FreezeFrame', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteFreezeFrame(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['FreezeFrame: Invalid/unexpected response'])

    def WriteFreezeFrame(self, value, qualifier, context):
        self.WriteStatusHelper('FreezeFrame', value, qualifier, context)

    def ReadFreezeFrame(self, qualifier, context):
        return self.ReadStatusHelper('FreezeFrame', qualifier, context)

    # Begin Menu
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Menu -> reserved preset 0x5F
    def _cmd_SetMenu(self, value, qualifier):
        """Set Menu
        value: Enum ('Toggle')
        qualifier: None
        """
        cmdString = self._PresetOpcode(0x5F)
        if self.__SafeToSet('Menu'):
            self.__SetHelper('Menu', cmdString, value, qualifier, 3)

    # Begin Identify
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Identify -> 81 C2 01 01 0A FF (custom command)
    def _cmd_SetIdentify(self, value, qualifier):
        """Set Identify
        value: Enum ('Identify')
        qualifier: None
        """
        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x01, 0x0A, 0xFF)
        if self.__SafeToSet('Identify'):
            self.__SetHelper('Identify', cmdString, value, qualifier, 3)

    # Begin Reboot
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Reboot -> reserved preset 0x63
    def _cmd_SetReboot(self, value, qualifier):
        """Set Reboot
        value: Enum ('Reboot')
        qualifier: None
        """
        cmdString = self._PresetOpcode(0x63)
        if self.__SafeToSet('Reboot'):
            self.__SetHelper('Reboot', cmdString, value, qualifier, 5)

    # Begin TrackingProfile
    ####################################################################################################################
    # Reserved presets 105-108 decimal (0x69-0x6C) = Tracking Profile 1-4.
    # I20 only. Source: reference/crestron-visca/COMMANDS.md section 10.
    # Crestron's driver declares SetTrackingFramingProfile as a preset recall
    # but supplies no preset value; the documentation supplies it.
    def _cmd_SetTrackingProfile(self, value, qualifier):
        """Set Tracking Profile
        value: Decimal (1 - 4)
        qualifier: None
        """
        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x68 + int(value))
            if self.__SafeToSet('TrackingProfile'):
                self.WriteTrackingProfile(value, qualifier, 'Emulated')
                self.__SetHelper('TrackingProfile', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetTrackingFramingProfile -> 81 C2 09 07 FF
    #   reply  y0 50 06 0x FF    x = 9..C
    # Crestron assembles those two bytes with ViscaAssemble2LowerNibbles, which
    # exists only as IL, then maps the result through
    # MapTrackingFramingProfileToPreset, whose domain is presets 0x69-0x6C =
    # Tracking Profile 1-4. Its reply rule admits exactly 06 09 to 06 0C, and
    # only the most-significant-first assembly lands in that domain
    # (0x6 << 4 | 0x9 = 0x69), so the order is fixed by Crestron's own rule and
    # map rather than assumed. Live from 20028.
    def _cmd_UpdateTrackingProfile(self, value, qualifier):
        """Update Tracking Profile
        value: Decimal
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x07, 0xFF)
        res = self.__UpdateHelper('TrackingProfile', cmdString, value, qualifier)
        if res:
            try:
                preset = self._FromNibbles(res[2:4])
                if not 0x69 <= preset <= 0x6C:
                    raise KeyError(preset)
                self.WriteTrackingProfile(preset - 0x68, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['TrackingProfile: Invalid/unexpected response'])

    def WriteTrackingProfile(self, value, qualifier, context):
        self.WriteStatusHelper('TrackingProfile', value, qualifier, context)

    def ReadTrackingProfile(self, qualifier, context):
        return self.ReadStatusHelper('TrackingProfile', qualifier, context)

    # Begin PresetZone
    ####################################################################################################################
    # Reserved presets 101-104 decimal (0x65-0x68) = Preset Zone 1-4. I20 only.
    def _cmd_SetPresetZone(self, value, qualifier):
        """Set Preset Zone
        value: Decimal (1 - 4)
        qualifier: None
        """
        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x64 + int(value))
            if self.__SafeToSet('PresetZone'):
                self.__SetHelper('PresetZone', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin TrackingShot
    ####################################################################################################################
    # Reserved presets 0 (Home Shot) and 1 (Tracking Shot).
    def _cmd_SetTrackingShot(self, value, qualifier):
        """Set Tracking Shot
        value: Enum ('Home'/'Tracking')
        qualifier: None
        """
        ValueStateValues = {
            'Home':     0x00,
            'Tracking': 0x01
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            if self.__SafeToSet('TrackingShot'):
                self.__SetHelper('TrackingShot', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

################################################################
### [PATCH E5] LIGHTBAR
###
### Command format 8x c1 ** ** ** ** ff - four payload bytes, one per
### lightbar segment. Crestron's driver declares this as
### SetIndicatorLight -> {Header} c1 {LedBar} FF with {LedBar} opaque; the
### documentation supplies the packing.
###
### Each payload byte is (brightness << 2) | colour, with
###     brightness  00 off, 01 dim, 10 medium, 11 bright
###     colour      00 green, 01 red, 11 yellow   (10 undefined)
### Half width leaves the two OUTER segments at brightness 00 while keeping
### their colour bits - which is why "half yellow" is 03 0F 0F 03 and not
### 00 0F 0F 00. That rule reproduces all 19 command strings printed in the
### documentation; test_i20_wire.py asserts every one of them.
###
### Segment geometry differs by model but the wire format does not: I20 has
### two outer segments of 4 lights and two inner of 3 (14 total); P20 has
### four segments of 4 (16 total).
################################################################

    _LIGHTBAR_COLOURS = {'Green': 0x0, 'Red': 0x1, 'Yellow': 0x3}
    _LIGHTBAR_BRIGHTNESS = {'Off': 0x0, 'Dim': 0x1, 'Medium': 0x2, 'Bright': 0x3}

    def _LightbarBytes(self, width, colour, brightness):
        """The four payload bytes for a width/colour/brightness combination."""
        c = self._LIGHTBAR_COLOURS[colour]
        b = self._LIGHTBAR_BRIGHTNESS[brightness]
        lit = (b << 2) | c
        if width == 'None':
            return [0x00, 0x00, 0x00, 0x00]
        if width == 'Half':
            return [c, lit, lit, c]
        return [lit, lit, lit, lit]

    # Begin IndicatorLight
    ####################################################################################################################
    def _cmd_SetIndicatorLight(self, value, qualifier):
        """Set Indicator Light (lightbar)
        value: Enum ('None'/'Half'/'Full')
        qualifier: {'Color': Enum, 'Brightness': Enum}
        """
        colour = qualifier.get('Color') if qualifier else None
        brightness = qualifier.get('Brightness') if qualifier else None

        if value == 'None':
            # Colour and brightness are irrelevant when nothing is lit, but the
            # qualifiers still have to be valid keys for the status tree.
            colour = colour or 'Green'
            brightness = 'Off'

        if (value in ['None', 'Half', 'Full']
                and colour in self._LIGHTBAR_COLOURS
                and brightness in self._LIGHTBAR_BRIGHTNESS):
            payload = self._LightbarBytes(value, colour, brightness)
            cmdString = pack('>7B', self.DeviceID, 0xC1, *(payload + [0xFF]))
            if self.__SafeToSet('IndicatorLight'):
                self.WriteIndicatorLight(value, qualifier, 'Emulated')
                self.__SetHelper('IndicatorLight', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def WriteIndicatorLight(self, value, qualifier, context):
        self.WriteStatusHelper('IndicatorLight', value, qualifier, context)

    def ReadIndicatorLight(self, qualifier, context):
        return self.ReadStatusHelper('IndicatorLight', qualifier, context)

################################################################
### [PATCH E6] INTELLIGENT SWITCHING (camera selection)
###
### The c2 command family, documented at
### reference/crestron-visca/COMMANDS.md section 9. Transport is TCP only
### for this family - the documentation does not offer serial, unlike the
### main and lightbar sets.
################################################################

    # Begin CameraOutput
    ####################################################################################################################
    # Call Camera Output:            8x c2 01 08 0Z ff   (Z = 1..5)
    # Resume Intelligent Switching:  8x c2 01 08 00 ff
    #
    # Value 0 is the SAME frame Intelligent Switching sends for Resume, so
    # until 20027 two commands could put one byte sequence on the wire and a
    # capture could not tell which had been used. Intelligent Switching already
    # offers Resume by name, so this range starts at 1 and the overlap is gone.
    def _cmd_SetCameraOutput(self, value, qualifier):
        """Set Camera Output
        value: Decimal (1 - 5)
        qualifier: None
        """
        if 1 <= int(value) <= 5:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08,
                             int(value), 0xFF)
            if self.__SafeToSet('CameraOutput'):
                self.WriteCameraOutput(value, qualifier, 'Emulated')
                self.__SetHelper('CameraOutput', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Get Output: 8x C2 09 08 FF
    #   VISCA-Intelligent-Switching-Commands.md:
    #     y0 50 01 0Z FF  switching on,   y0 50 00 0Z FF  switching off
    # The camera is the second payload byte; reading the first gave the
    # switching flag instead (found by experiments/loopback). From 20028 that
    # first byte is not discarded: it is Intelligent Switching's status, so one
    # reply answers both commands.
    def _OutputInquiry(self, command, value, qualifier):
        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x08, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParseOutput)

    def _ParseOutput(self, res, qualifier):
        camera = res[3] & 0x0F
        self.WriteCameraOutput(camera, qualifier, 'Live')
        switching = {0x01: 'Resume', 0x00: 'Pause'}[res[2]]
        self.WriteIntelligentSwitching(switching, qualifier, 'Live')
        return camera, switching

    def _cmd_UpdateCameraOutput(self, value, qualifier):
        """Update Camera Output
        value: Decimal
        qualifier: None
        """
        self._OutputInquiry('CameraOutput', value, qualifier)

    def WriteCameraOutput(self, value, qualifier, context):
        self.WriteStatusHelper('CameraOutput', value, qualifier, context)

    def ReadCameraOutput(self, qualifier, context):
        return self.ReadStatusHelper('CameraOutput', qualifier, context)

    # Begin IntelligentSwitching
    ####################################################################################################################
    # Pause:  8x c2 01 0B 00 ff        Resume: 8x c2 01 08 00 ff
    def _cmd_SetIntelligentSwitching(self, value, qualifier):
        """Set Intelligent Switching
        value: Enum ('Resume'/'Pause')
        qualifier: None
        """
        if value == 'Pause':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x0B, 0x00, 0xFF)
        elif value == 'Resume':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08, 0x00, 0xFF)
        else:
            self.Discard('Invalid Command')
            return

        if self.__SafeToSet('IntelligentSwitching'):
            self.WriteIntelligentSwitching(value, qualifier, 'Emulated')
            self.__SetHelper('IntelligentSwitching', cmdString, value, qualifier, 3)

    # Get Output's first payload byte, shared with Camera Output above.
    def _cmd_UpdateIntelligentSwitching(self, value, qualifier):
        """Update Intelligent Switching
        value: Enum
        qualifier: None
        """
        self._OutputInquiry('IntelligentSwitching', value, qualifier)

    def WriteIntelligentSwitching(self, value, qualifier, context):
        self.WriteStatusHelper('IntelligentSwitching', value, qualifier, context)

    def ReadIntelligentSwitching(self, qualifier, context):
        return self.ReadStatusHelper('IntelligentSwitching', qualifier, context)

    # Begin CameraConnectionStatus
    ####################################################################################################################
    # Check Connection Status: 8x c2 09 0d 0Z ff
    #   Disconnect: Y0 50 00 00 FF     Connect: Y0 50 00 01 FF
    def _cmd_UpdateCameraConnectionStatus(self, value, qualifier):
        """Update Camera Connection Status
        value: Enum
        qualifier: {'Camera' : Decimal 2-5}
        """
        try:
            camera = int(qualifier['Camera'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if not 2 <= camera <= 5:
            self.Discard('Invalid Command')
            return

        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x09, 0x0D, camera, 0xFF)
        res = self.__UpdateHelper('CameraConnectionStatus', cmdString, value, qualifier)
        if res:
            try:
                value = 'Connected' if res[3] else 'Disconnected'
                self.WriteCameraConnectionStatus(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['CameraConnectionStatus: Invalid/unexpected response'])

    def WriteCameraConnectionStatus(self, value, qualifier, context):
        self.WriteStatusHelper('CameraConnectionStatus', value, qualifier, context)

    def ReadCameraConnectionStatus(self, qualifier, context):
        return self.ReadStatusHelper('CameraConnectionStatus', qualifier, context)

################################################################
### [PATCH E7] PARITY WITH CRESTRON'S I20 DRIVER (v1.6)
###
### Commands Crestron's driver has and 20027 did not. Every request is
### Crestron's own template (i20_wire_table.txt), every reply rule is
### Crestron's Responses entry, and every range is a Crestron controller's
### declared Min/Max (experiments/skeleton_i20/CRESTRON_PARITY.md).
###
### Left out on purpose, and why (CRESTRON_PARITY.md has the detail):
###   Privacy Enable/Disable  driver behaviour, not a camera command: stop,
###                           remember the tilt, point at the ceiling, return.
###                           Pan Tilt Angle does it from a program.
###   Press-and-hold menu     the same bytes as Zoom Tele/Wide/Stop and the
###                           Pan Tilt arrows at speed 1, sent with Menu open.
###   Field Of View           its conversion is a polynomial Crestron supplies
###                           only as IL (OverridePolynomial).
###   PTZ Super Operation     its operation codes are declared nowhere.
###   Exposure Comp Up/Down   Exposure Compensation sets the level directly.
################################################################

    # Begin ExposureCompensationMode
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetExposureCompensationMode -> 81 01 04 3E {OnOff} FF
    #                         GetExposureCompensationMode -> 81 09 04 3E FF
    # MapBooleanToViscaOnOff both ways: On = 0x02, Off = 0x03.
    def _cmd_SetExposureCompensationMode(self, value, qualifier):
        """Set Exposure Compensation Mode
        value: Enum ('On'/'Off')
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x3E,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('ExposureCompensationMode'):
                self.WriteExposureCompensationMode(value, qualifier, 'Emulated')
                self.__SetHelper('ExposureCompensationMode', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateExposureCompensationMode(self, value, qualifier):
        """Update Exposure Compensation Mode
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x3E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensationMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteExposureCompensationMode(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['ExposureCompensationMode: Invalid/unexpected response'])

    def WriteExposureCompensationMode(self, value, qualifier, context):
        self.WriteStatusHelper('ExposureCompensationMode', value, qualifier, context)

    def ReadExposureCompensationMode(self, qualifier, context):
        return self.ReadStatusHelper('ExposureCompensationMode', qualifier, context)

    # Begin ExposureCompensation
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetExposureCompensation -> 81 01 04 4E 00 00 {Y2} {Y1} FF
    #                         GetExposureCompensation -> 81 09 04 4E FF
    #   reply  y0 50 00 00 0p 0q FF
    # Range 0-14 from Crestron's ExposureCompensation controller. The
    # documentation's table reads 0x00 = -7 EV, 0x07 = 0 EV, 0x0E = +7 EV.
    # It only acts in auto exposure: Crestron's driver blocks it otherwise.
    def _cmd_SetExposureCompensation(self, value, qualifier):
        """Set Exposure Compensation
        value: Decimal (0 - 14)
        qualifier: None
        """
        if 0 <= int(value) <= 14:
            cmdString = pack('>9B', self.DeviceID, 0x01, 0x04, 0x4E, 0x00, 0x00,
                             *(self._Nibbles(value, 2) + [0xFF]))
            if self.__SafeToSet('ExposureCompensation'):
                self.WriteExposureCompensation(value, qualifier, 'Emulated')
                self.__SetHelper('ExposureCompensation', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateExposureCompensation(self, value, qualifier):
        """Update Exposure Compensation
        value: Decimal
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x4E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensation', cmdString, value, qualifier)
        if res:
            try:
                value = self._FromNibbles(res[2:6])
                if not 0 <= value <= 14:
                    raise KeyError(value)
                self.WriteExposureCompensation(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['ExposureCompensation: Invalid/unexpected response'])

    def WriteExposureCompensation(self, value, qualifier, context):
        self.WriteStatusHelper('ExposureCompensation', value, qualifier, context)

    def ReadExposureCompensation(self, qualifier, context):
        return self.ReadStatusHelper('ExposureCompensation', qualifier, context)

    # Begin FocusPosition
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetFocusPosition -> 81 01 04 48 {Y4} {Y3} {Y2} {Y1} FF
    #                         GetFocusPosition -> 81 09 04 48 FF
    #   reply  y0 50 0p 0q 0r 0s FF
    # Crestron's FocusPosition range differs by model (its
    # FeedbackForZoomAndFocusRanges rules): IV-CAM-I20 12224-17114,
    # IV-CAM-I12 15084-20664. This driver is not told its model, so it accepts
    # the union. The camera rejects focus commands while auto focus is on.
    def _cmd_SetFocusPosition(self, value, qualifier):
        """Set Focus Position
        value: Decimal (12224 - 20664)
        qualifier: None
        """
        if 12224 <= int(value) <= 20664:
            cmdString = pack('>9B', self.DeviceID, 0x01, 0x04, 0x48,
                             *(self._Nibbles(value, 4) + [0xFF]))
            if self.__SafeToSet('FocusPosition'):
                self.WriteFocusPosition(value, qualifier, 'Emulated')
                self.__SetHelper('FocusPosition', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateFocusPosition(self, value, qualifier):
        """Update Focus Position
        value: Decimal
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x48, 0xFF)
        res = self.__UpdateHelper('FocusPosition', cmdString, value, qualifier)
        if res:
            try:
                value = self._FromNibbles(res[2:6])
                self.WriteFocusPosition(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['FocusPosition: Invalid/unexpected response'])

    def WriteFocusPosition(self, value, qualifier, context):
        self.WriteStatusHelper('FocusPosition', value, qualifier, context)

    def ReadFocusPosition(self, qualifier, context):
        return self.ReadStatusHelper('FocusPosition', qualifier, context)

    # Begin OnePushAutoFocus
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: OnePushAutoFocus -> 81 01 04 18 01 FF
    # (CAM_Focus One Push Trigger in the VISCA table.)
    def _cmd_SetOnePushAutoFocus(self, value, qualifier):
        """Set One Push Auto Focus
        value: Enum ('Trigger')
        qualifier: None
        """
        cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x18, 0x01, 0xFF)
        if self.__SafeToSet('OnePushAutoFocus'):
            self.__SetHelper('OnePushAutoFocus', cmdString, value, qualifier, 3)

    # Begin AutoFocusBehavior
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetAutoFocusBehavior -> 81 C2 01 02 {v} FF
    #                         GetAutoFocusBehavior -> 81 C2 09 02 FF
    #   reply  y0 50 00 0v FF
    # MapAutoFocusBehavior: global 0x00, center 0x01, face 0x04.
    def _cmd_SetAutoFocusBehavior(self, value, qualifier):
        """Set Auto Focus Behavior
        value: Enum ('Global'/'Center'/'Face')
        qualifier: None
        """
        ValueStateValues = {
            'Global':   0x00,
            'Center':   0x01,
            'Face':     0x04
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x02,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('AutoFocusBehavior'):
                self.WriteAutoFocusBehavior(value, qualifier, 'Emulated')
                self.__SetHelper('AutoFocusBehavior', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAutoFocusBehavior(self, value, qualifier):
        """Update Auto Focus Behavior
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x00: 'Global',
            0x01: 'Center',
            0x04: 'Face'
        }

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x02, 0xFF)
        res = self.__UpdateHelper('AutoFocusBehavior', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteAutoFocusBehavior(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['AutoFocusBehavior: Invalid/unexpected response'])

    def WriteAutoFocusBehavior(self, value, qualifier, context):
        self.WriteStatusHelper('AutoFocusBehavior', value, qualifier, context)

    def ReadAutoFocusBehavior(self, qualifier, context):
        return self.ReadStatusHelper('AutoFocusBehavior', qualifier, context)

    # Begin AutoFocusSensitivity
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetAutoFocusSensitivity -> 81 C2 01 03 {v} FF
    #                         GetAutoFocusSensitivity -> 81 C2 09 03 FF
    #   reply  y0 50 00 0v FF
    # Range 1-3 from Crestron's AutoFocusSensitivity controller; the value is
    # sent as a byte (AsByte) and read back raw (FromBytesToUInt).
    def _cmd_SetAutoFocusSensitivity(self, value, qualifier):
        """Set Auto Focus Sensitivity
        value: Decimal (1 - 3)
        qualifier: None
        """
        if 1 <= int(value) <= 3:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x03, int(value), 0xFF)
            if self.__SafeToSet('AutoFocusSensitivity'):
                self.WriteAutoFocusSensitivity(value, qualifier, 'Emulated')
                self.__SetHelper('AutoFocusSensitivity', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAutoFocusSensitivity(self, value, qualifier):
        """Update Auto Focus Sensitivity
        value: Decimal
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x03, 0xFF)
        res = self.__UpdateHelper('AutoFocusSensitivity', cmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                if not 1 <= value <= 3:
                    raise KeyError(value)
                self.WriteAutoFocusSensitivity(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['AutoFocusSensitivity: Invalid/unexpected response'])

    def WriteAutoFocusSensitivity(self, value, qualifier, context):
        self.WriteStatusHelper('AutoFocusSensitivity', value, qualifier, context)

    def ReadAutoFocusSensitivity(self, qualifier, context):
        return self.ReadStatusHelper('AutoFocusSensitivity', qualifier, context)

    # Begin AutoPrivacyMode
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetAutoPrivacyMode -> 81 01 0E 24 26 00 {OnOff} FF
    #                         GetAutoPrivacyMode -> 81 09 0E 24 26 FF
    #   reply  y0 50 00 0v FF
    # MapBooleanToBinaryOnOff: On = 0x01, Off = 0x00 (not VISCA's 02/03).
    # The camera's own privacy mode. Crestron's driver asks for it to be off,
    # because a camera in privacy mode answers no VISCA command.
    def _cmd_SetAutoPrivacyMode(self, value, qualifier):
        """Set Auto Privacy Mode
        value: Enum ('On'/'Off')
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
        }

        if value in ValueStateValues:
            cmdString = pack('>8B', self.DeviceID, 0x01, 0x0E, 0x24, 0x26, 0x00,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('AutoPrivacyMode'):
                self.WriteAutoPrivacyMode(value, qualifier, 'Emulated')
                self.__SetHelper('AutoPrivacyMode', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAutoPrivacyMode(self, value, qualifier):
        """Update Auto Privacy Mode
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        cmdString = pack('>6B', self.DeviceID, 0x09, 0x0E, 0x24, 0x26, 0xFF)
        res = self.__UpdateHelper('AutoPrivacyMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteAutoPrivacyMode(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['AutoPrivacyMode: Invalid/unexpected response'])

    def WriteAutoPrivacyMode(self, value, qualifier, context):
        self.WriteStatusHelper('AutoPrivacyMode', value, qualifier, context)

    def ReadAutoPrivacyMode(self, qualifier, context):
        return self.ReadStatusHelper('AutoPrivacyMode', qualifier, context)

    # Begin AutoSoftwareUpdate
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetAutoSoftwareUpdate -> 81 C2 01 04 {OnOff} FF
    #                         GetAutoSoftwareUpdate -> 81 C2 09 04 FF
    #   reply  y0 50 00 0v FF
    # MapBooleanToBinaryOnOff: On = 0x01, Off = 0x00. Crestron polls it every
    # 30 s, the slowest poll in its driver.
    def _cmd_SetAutoSoftwareUpdate(self, value, qualifier):
        """Set Auto Software Update
        value: Enum ('On'/'Off')
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x01,
            'Off':  0x00
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x04,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('AutoSoftwareUpdate'):
                self.WriteAutoSoftwareUpdate(value, qualifier, 'Emulated')
                self.__SetHelper('AutoSoftwareUpdate', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateAutoSoftwareUpdate(self, value, qualifier):
        """Update Auto Software Update
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x04, 0xFF)
        res = self.__UpdateHelper('AutoSoftwareUpdate', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteAutoSoftwareUpdate(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['AutoSoftwareUpdate: Invalid/unexpected response'])

    def WriteAutoSoftwareUpdate(self, value, qualifier, context):
        self.WriteStatusHelper('AutoSoftwareUpdate', value, qualifier, context)

    def ReadAutoSoftwareUpdate(self, qualifier, context):
        return self.ReadStatusHelper('AutoSoftwareUpdate', qualifier, context)

    # Begin DeviceModel / RomVersion
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: GetDeviceInformation -> 81 09 00 02 FF
    #   reply  y0 50 00 01 mn pq rs tu vw FF
    #          model code mn pq, ROM version rs tu, socket vw (CAM_VersionInq)
    # MapModelCodeToModel: 05 05 IV-CAM-I20, 05 06 IV-CAM-I12, 05 07 IV-CAM-P20,
    # 05 08 IV-CAM-P12, anything else Unknown. Crestron turns the ROM version
    # into text with FormatRomVersion, which exists only as IL, so this reports
    # the two bytes as the 16-bit number they are rather than guess its format.
    _MODEL_CODES = {
        (0x05, 0x05): 'IV-CAM-I20',
        (0x05, 0x06): 'IV-CAM-I12',
        (0x05, 0x07): 'IV-CAM-P20',
        (0x05, 0x08): 'IV-CAM-P12'
    }

    def _VersionInquiry(self, command, value, qualifier):
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x00, 0x02, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParseVersion)

    def _ParseVersion(self, res, qualifier):
        model = self._MODEL_CODES.get((res[4], res[5]), 'Unknown')
        rom = (res[6] << 8) | res[7]
        self.WriteDeviceModel(model, qualifier, 'Live')
        self.WriteRomVersion(rom, qualifier, 'Live')
        return model, rom

    def _cmd_UpdateDeviceModel(self, value, qualifier):
        """Update Device Model
        value: Enum
        qualifier: None
        """
        self._VersionInquiry('DeviceModel', value, qualifier)

    def WriteDeviceModel(self, value, qualifier, context):
        self.WriteStatusHelper('DeviceModel', value, qualifier, context)

    def ReadDeviceModel(self, qualifier, context):
        return self.ReadStatusHelper('DeviceModel', qualifier, context)

    def _cmd_UpdateRomVersion(self, value, qualifier):
        """Update ROM Version
        value: Decimal
        qualifier: None
        """
        self._VersionInquiry('RomVersion', value, qualifier)

    def WriteRomVersion(self, value, qualifier, context):
        self.WriteStatusHelper('RomVersion', value, qualifier, context)

    def ReadRomVersion(self, qualifier, context):
        return self.ReadStatusHelper('RomVersion', qualifier, context)

    # Begin PanSpeedMaxStatus / TiltSpeedMaxStatus
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: GetPanTiltSpeedMax -> 81 09 06 11 FF
    #   reply  y0 50 ww zz FF    ww pan, zz tilt: one whole byte each, not
    #                            nibbles (Pan-tiltMaxSpeedInq)
    def _SpeedMaxInquiry(self, command, value, qualifier):
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x11, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParseSpeedMax)

    def _ParseSpeedMax(self, res, qualifier):
        speeds = (res[2], res[3])
        self.WritePanSpeedMaxStatus(speeds[0], qualifier, 'Live')
        self.WriteTiltSpeedMaxStatus(speeds[1], qualifier, 'Live')
        return speeds

    def _cmd_UpdatePanSpeedMaxStatus(self, value, qualifier):
        """Update Pan Speed Max Status
        value: Decimal
        qualifier: None
        """
        self._SpeedMaxInquiry('PanSpeedMaxStatus', value, qualifier)

    def WritePanSpeedMaxStatus(self, value, qualifier, context):
        self.WriteStatusHelper('PanSpeedMaxStatus', value, qualifier, context)

    def ReadPanSpeedMaxStatus(self, qualifier, context):
        return self.ReadStatusHelper('PanSpeedMaxStatus', qualifier, context)

    def _cmd_UpdateTiltSpeedMaxStatus(self, value, qualifier):
        """Update Tilt Speed Max Status
        value: Decimal
        qualifier: None
        """
        self._SpeedMaxInquiry('TiltSpeedMaxStatus', value, qualifier)

    def WriteTiltSpeedMaxStatus(self, value, qualifier, context):
        self.WriteStatusHelper('TiltSpeedMaxStatus', value, qualifier, context)

    def ReadTiltSpeedMaxStatus(self, qualifier, context):
        return self.ReadStatusHelper('TiltSpeedMaxStatus', qualifier, context)

### END AUTO GENERATION OF COMMAND DEF
################################################################

    def __CheckResponseForErrors(self, sourceCmdName, response):
        """Check Response For Errors
        Called by all SendAndWait calls to the device.
        Device will always have a response...confirmation, errors or answer to queries

        """
        if response and len(response) == 4:
            # 1 Beyond PTZ-IP12-IP20 Manual, page 22
            error_map = {
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }

            if response[1] & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map.get(response[2], 'Unknown Error'))])
                response = ''

        return response

    def __SafeToSet(self, command):
        powerstatus = self.ReadPower(None, 'Live')
        if powerstatus in ['Off', 'Internal Power Circuit Error'] and command not in ['Power']:
            self.Discard('Inappropriate Command')
            return False
        else:
            return True

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0.1):
        """Set Helper
        This function is used to determine how to send.

        """
        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
            if queryDisallowTime > 0:
                self.StartQueryDelayTimer(queryDisallowTime)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        """Update Helper
        This function is used to determine how to send.

        """
        if self.QueryDelayTimerIsRunning():
            self.Discard('Device Is Busy')
            return ''
        elif self.Unidirectional == 'True':
            self.Discard('Inappropriate Command')
            return ''
        else:
            powerstatus = self.ReadPower(qualifier, 'Live')
            if powerstatus in ['Off', 'Internal Power Circuit Error', None] and command not in ['Power']:
                self.Discard('Inappropriate Command')
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
                self.WriteStatusHelper(command, value, qualifier, 'UpdateTime')
                if not res:
                    if 'Power' == command:
                        self.WriteDeviceResponseStatus('Bad', None, 'Live')
                    return ''
                else:
                    self.WriteDeviceResponseStatus('Good', None, 'Live')
                    return self.__CheckResponseForErrors(command, res)
     
    def OnConnected(self):
        '''
        On Connected
        This callback will be set by the firmware when a device has connected or
        reconnected to the device.  It's called after a successful response (sync)
        or matchstring (async) via the self.DriverResponseStatus property

        '''
        pass

    def OnDisconnected(self):
        '''
        On Disconnected
        This callback will be set by the firmware when a device has not responded
        or malformed responed for <n> seconds as indicated in the driver
        descriptor.  Behavior is to set all status to their uninitialized state.

        '''
        self.__ResetLiveStatus()

################################################################
### HELPER METHODS SECTION
################################################################

    def WriteStatusHelper(self, command, value, qualifier, context):
        '''
        Write Status Helper
        Wrapper method to manage setting/posting Live and Emulated status

        '''
        Command = self.Commands[command]
        if Command['Live'] or Command['Emulated']:
            Status = Command['Status']
            with self.Mutex():
                if 'Parameters' in Command:
                    for Parameter in Command['Parameters']: 
                        try:
                            Status = Status[qualifier[Parameter]]
                        except KeyError:
                            if Parameter in qualifier:
                                Status[qualifier[Parameter]] = {}
                                Status = Status[qualifier[Parameter]]
                            else:
                                self.Error(['Invalid parameter(s): {0}'.format(qualifier)])
                                return
                try:
                    if context in ['Live', 'Emulated']:
                        Status['TimeStamps'][context] = ExtronTime(time.monotonic())
                        if Status[context] != value:
                            Status[context] = value
                            self.PostNewStatusEx(command, value, qualifier, context)
                    elif context == 'UpdateTime':
                        try:
                            Status['TimeStamps']['Update'] = ExtronTime(time.monotonic())
                        except KeyError:
                            Status['TimeStamps'] = {'Update': ExtronTime(time.monotonic())}
                    elif context == 'Meta':
                        Status['Meta'] = value
                    
                except:
                    Status['Emulated'] = value
                    if 'TimeStamps' not in Status:
                        Status['TimeStamps'] = {}
                    Status['TimeStamps']['Emulated'] = ExtronTime(time.monotonic())
                    self.PostNewStatusEx(command, value, qualifier, 'Emulated')
                    if context == 'Live':
                        Status['Live'] = value
                        Status['TimeStamps']['Live'] = ExtronTime(time.monotonic())
                        self.PostNewStatusEx(command, value, qualifier, 'Live')
                    else:
                        Status['Live'] = None
                        Status['TimeStamps']['Live'] = None
        else:
            self.Error(['Command, {0}, does not have status.'.format(command)])
            return

    def ReadStatusHelper(self, command, qualifier, context):
        '''
        Read Status Helper
        Wrapper method to return current status Live or Emulated

        '''
        Command = self.Commands[command]
        if Command['Live'] or Command['Emulated']:
            Status = Command['Status']
            with self.Mutex():
                if 'Parameters' in Command:
                    for Parameter in Command['Parameters']: 
                        try:
                            Status = Status[qualifier[Parameter]]
                        except KeyError:
                            return None
                try:
                    return Status[context]
                except:
                    return None
        else:
            self.Error(['Command, {0}, does not have status.'.format(command)])
            return

    def __StatusItems(self, dictionary):
        '''Iterator Function to 'yield' all of the Live/Emulated pairs

        '''
        for k, v in dictionary.items():
            if k == 'Live' and not isinstance(dictionary['Live'], dict) and not isinstance(dictionary['Live'], ExtronTime):
                yield [], dictionary
            elif isinstance(v, dict):
                for subkey, result in self.__StatusItems(v):
                    yield [k]+subkey, result

    def _cmd_SetSyncEmulatedStatus(self, value, qualifier):
        """
        Synchronize All Emulated Status
        This command is issued by the automation script to cause a driver to sync 
        all Emulated Feedback status to the authoritative Live feedback information.
        For each Emulated Feedback field that is out of date, change notification 
        should be generated.
        value:  None
        qualifier:  None

        """
        with self.Mutex():
            if value in self.Commands:
                Command = self.Commands[value]
                if Command['Live'] and Command['Emulated']:
                    Status = Command['Status']
                    if 'Parameters' in Command:
                        for Parameter in Command['Parameters']: 
                            try:
                                Status = Status[qualifier[Parameter]]
                            except KeyError:
                                if Parameter not in qualifier:
                                    self.Error(['Invalid parameter(s): {0}'.format(qualifier)])
                                    return
                    try:
                        if Status['Live'] is not None and Status['Live'] != Status['Emulated'] and Status['TimeStamps']['Live'] > Status['TimeStamps']['Emulated']:
                            Status['Emulated'] = Status['Live']
                            self.PostNewStatusEx(value, Status['Live'], qualifier, 'Emulated')
                    except:
                        pass
            else:
                self.Error(['Invalid Command: {0}'.format(value)])

    def StatusRefresh(self):
        """
        Status Refresh
        This command is called by the automation script when it needs a driver to
        to generate a Refresh of status for soft clients.

        """
        self.PostNewStatusEx('RefreshBegin', None, None, 'Live')
        with self.Mutex():
            for command in self.Commands:
                Command = self.Commands[command]
                for Parameters, Status in self.__StatusItems(Command['Status']):
                    qualifier = {}
                    for Parameter in range(len(Parameters)):
                        qualifier[Command['Parameters'][Parameter]] = Parameters[Parameter]
                    self.PostNewStatusEx(command, Status['Live'], qualifier, 'LiveRefresh')
                    self.PostNewStatusEx(command, Status['Emulated'], qualifier, 'EmulatedRefresh')
        super().StatusRefresh()
        self.PostNewStatusEx('RefreshComplete', None, None, 'Live')
    
    def __ResetLiveStatus(self):
        '''
        Reset Status to Uninitialized
        This function is call when OnDisconnected is call to reset all the Live status.

        '''
        with self.Mutex():
            for command in self.Commands:
                Command = self.Commands[command]
                if Command['Live']:
                    for _, Status in self.__StatusItems(Command['Status']):
                        Status['Live'] = None

    #Parent Class overloads
    def SendAndWait(self, data, timeout, **kwds):
        """Send and Wait
        Overload to handle bytes translation. If the data is a string then the data returned
        from the device will be a string. If the data sent is a byte string, then
        the data returned from the device will be a byte string.
        
        """        
        if isinstance(data, str):
            data = data.encode()
            IsString = True
        else:
            IsString = False
        try:
            kwds['deliTag'] = kwds['deliTag'].encode()
        except:
            pass
        if IsString:
            check = super().SendAndWait(data, timeout, **kwds)
            if check:
                return check.decode()
            else:
                return ''
        else:
            return super().SendAndWait(data, timeout, **kwds)

    def Send(self, data, **kwds):
        """Send
        Overload to handle bytes translation.

        """        
        if isinstance(data, str):
            data = data.encode()
        super().Send(data, **kwds)


class ExtronTime(float):
    pass
