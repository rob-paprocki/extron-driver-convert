from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from extronlib import Version

try:
    from Extron import Platform
    platform = Platform()
except ImportError:
    platform = 'Pro'

minimumVersion = (3,4,6)
version = tuple(int(i) for i in Version().split('.'))

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'sysop'
        self.devicePassword = 'freeporttech'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BackgroundBorderColor': {'Parameters':['Red','Green','Blue','Transparency'], 'Status': {}},
            'BackgroundBorderColorStatus': { 'Status': {}},
            'BackgroundBorderWidth': { 'Status': {}},
            'BackgroundFillColor': {'Parameters': ['Red', 'Green', 'Blue'], 'Status': {}},
            'BackgroundVisible': { 'Status': {}},
            'ClockDateFontColor': {'Parameters':['Clock','Red','Green','Blue'], 'Status': {}},
            'ClockDateVisible': {'Parameters': ['Clock'], 'Status': {}},
            'ClockDisplayType': {'Parameters': ['Clock'], 'Status': {}},
            'ClockFontColor': {'Parameters':['Clock','Type','Red','Green','Blue'], 'Status': {}},
            'ClockNameFontColor': {'Parameters': ['Clock', 'Red', 'Green', 'Blue'], 'Status': {}},
            'ClockNameTextCommand': {'Parameters': ['Clock'], 'Status': {}},
            'ClockTimezoneCommand': {'Parameters': ['Clock'], 'Status': {}},
            'ClockVisible': {'Parameters': ['Clock'], 'Status': {}},
            'IconAnimationSpeed': {'Parameters': ['Icon', 'State'], 'Status': {}},
            'IconAnimationType': {'Parameters': ['Icon', 'State'], 'Status': {}},
            'IconColor': {'Parameters': ['Icon', 'State', 'Red', 'Green', 'Blue'], 'Status': {}},
            'IconFontColor': {'Parameters': ['Icon', 'State', 'Red', 'Green', 'Blue'], 'Status': {}},
            'IconRegion': {'Parameters': ['Icon'], 'Status': {}},
            'IconState': {'Parameters': ['Icon'], 'Status': {}},
            'IconTextCommand': {'Parameters': ['Icon', 'State'], 'Status': {}},
            'IconVisible': {'Parameters': ['Icon'], 'Status': {}},
            'LayoutConfiguration': { 'Status': {}},
            'LogoVisible': {'Parameters':['Logo'], 'Status': {}},
            'MessageAnimationSpeed': {'Parameters': ['Message'], 'Status': {}},
            'MessageAnimationType': {'Parameters': ['Message'], 'Status': {}},
            'MessageFontColor': {'Parameters': ['Message', 'Red', 'Green', 'Blue'], 'Status': {}},
            'MessageFontSize': {'Parameters': ['Message'], 'Status': {}},
            'MessageTextCommand': {'Parameters': ['Message'], 'Status': {}},
            'MessageVisible': {'Parameters': ['Message'], 'Status': {}},
            'PresetRecallCommand': { 'Status': {}},
            'SetupDatetimeCommand': {'Parameters':['Type'], 'Status': {}},
            'SetupDatetimeStatus': {'Parameters':['Type'], 'Status': {}},
        }

        self.Authenticated = 'Needed'
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'feature background borderColor: (#\w{8})'), self.__MatchBackgroundBorderColorStatus, None)
            self.AddMatchString(re.compile(b'feature background borderWidth: (\d{1,3})'), self.__MatchBackgroundBorderWidth, None)
            self.AddMatchString(re.compile(b'feature background visible: (true|false)'), self.__MatchBackgroundVisible, None)
            self.AddMatchString(re.compile(b'feature clock ([0-4]) dateVisible: (true|false)'), self.__MatchClockDateVisible, None)
            self.AddMatchString(re.compile(b'feature clock ([0-4]) visible: (true|false)'), self.__MatchClockVisible, None)
            self.AddMatchString(re.compile(b'feature icon ([0-4]) visible: (true|false)'), self.__MatchIconVisible, None)
            self.AddMatchString(re.compile(b'feature layout id: ([0-4])'), self.__MatchLayoutConfiguration, None)
            self.AddMatchString(re.compile(b'feature logo ([01]) visible: (true|false)'), self.__MatchLogoVisible, None)
            self.AddMatchString(re.compile(b'feature message ([0-2]) visible: (true|false)'), self.__MatchMessageVisible, None)
            self.AddMatchString(re.compile(b'setup datetime time: ([01]\d/[0-3]\d/\d{4} [01]\d:[0-5]\d:[0-5]\d)'), self.__MatchSetupDatetimeStatus, 'Time')
            self.AddMatchString(re.compile(b'setup datetime ntp 0: (\d{3}.\d{3}.\d{3}.\d{3})'), self.__MatchSetupDatetimeStatus, 'NTP')
            self.AddMatchString(re.compile(b'Invalid command|Invalid value: .*\r|Invalid path: .*\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'(Welcome to Mercury!|Login incorrect)'), self.__MatchLogin, None)

    def SetUsername(self, value, qualifier):

        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def SetPassword(self, value, qualifier):

        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchUsername(self, match, tag):

        self.SetUsername( None, None)

    def __MatchPassword(self, match, tag):

        self.SetPassword( None, None)

    def __MatchLogin(self, match, tag):

        if 'Welcome' in match.group(1).decode():
            self.Authenticated = 'Not Needed'
        else:
            self.Authenticated = 'Needed'
            self.Error(['Incorrect Login information.'])

    def SetBackgroundBorderColor(self, value, qualifier):

        if 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255 and 0 <= qualifier['Transparency'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}{transparency:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'],
                                                                  transparency=qualifier['Transparency'])
            BackgroundBorderColorCmdString = 'set feature background borderColor: {fillColor}\r\n'.format(fillColor=rgb_values)
            self.__SetHelper('BackgroundBorderColor', BackgroundBorderColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundBorderColor')

    def UpdateBackgroundBorderColorStatus(self, value, qualifier):

        BackgroundBorderColorStatusCmdString = 'get feature background borderColor\r\n'
        self.__UpdateHelper('BackgroundBorderColorStatus', BackgroundBorderColorStatusCmdString, value, qualifier)

    def __MatchBackgroundBorderColorStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('BackgroundBorderColorStatus', value, None)

    def SetBackgroundBorderWidth(self, value, qualifier):

        if 0 <= value <= 255:
            BackgroundBorderWidthCmdString = 'set feature background borderWidth: {}\r\n'.format(value)
            self.__SetHelper('BackgroundBorderWidth', BackgroundBorderWidthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundBorderWidth')

    def UpdateBackgroundBorderWidth(self, value, qualifier):

        BackgroundBorderWidthCmdString = 'get feature background borderWidth\r\n'
        self.__UpdateHelper('BackgroundBorderWidth', BackgroundBorderWidthCmdString, value, qualifier)

    def __MatchBackgroundBorderWidth(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 255:
            self.WriteStatus('BackgroundBorderWidth', value, None)

    def SetBackgroundFillColor(self, value, qualifier):

        if 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            BackgroundFillColorCmdString = 'set feature background fillColor: {fillColor}\r\n'.format(fillColor=rgb_values)
            self.__SetHelper('BackgroundFillColor', BackgroundFillColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundFillColor')

    def SetBackgroundVisible(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'true',
            'Off' : 'false'
        }

        if value in ValueStateValues:
            BackgroundVisibleCmdString = 'set feature background visible: {visible}\r\n'.format(visible=ValueStateValues[value])
            self.__SetHelper('BackgroundVisible', BackgroundVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBackgroundVisible')

    def UpdateBackgroundVisible(self, value, qualifier):

        BackgroundVisibleCmdString = 'get feature background visible\r\n'
        self.__UpdateHelper('BackgroundVisible', BackgroundVisibleCmdString, value, qualifier)

    def __MatchBackgroundVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BackgroundVisible', value, None)

    def SetClockDateFontColor(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])

        if 1 <= clock_idx <= 5 and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            ClockDateFontColorCmdString = 'set feature clock {index} dateFont color: {color}\r\n'.format(index=clock_idx-1, color=rgb_values)
            self.__SetHelper('ClockDateFontColor', ClockDateFontColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockDateFontColor')

    def SetClockDateVisible(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }

        clock_idx = int(qualifier['Clock'])

        if value in ValueStateValues and 1 <= clock_idx <= 5:
            ClockDateVisibleCmdString = 'set feature clock {index} dateVisible: {dateVisible}\r\n'.format(index=clock_idx-1, dateVisible=ValueStateValues[value])
            self.__SetHelper('ClockDateVisible', ClockDateVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockDateVisible')

    def UpdateClockDateVisible(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])

        if 1 <= clock_idx <= 5:
            ClockDateVisibleCmdString = 'get feature clock {} dateVisible\r\n'.format(clock_idx-1)
            self.__UpdateHelper('ClockDateVisible', ClockDateVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateClockDateVisible')

    def __MatchClockDateVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        qualifier = {'Clock' : str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ClockDateVisible', value, qualifier)

    def SetClockDisplayType(self, value, qualifier):

        ValueStateValues = {
            'Analog' : 'analog',
            'Digital': 'digital',
            'Both'   : 'both'
        }

        clock_idx = int(qualifier['Clock'])

        if value in ValueStateValues and 1 <= clock_idx <= 5:
            ClockDisplayTypeCmdString = 'set feature clock {index} displayType: {displayType}\r\n'.format(index=clock_idx-1, displayType=ValueStateValues[value])
            self.__SetHelper('ClockDisplayType', ClockDisplayTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockDisplayType')

    def SetClockFontColor(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])

        if 1 <= clock_idx <= 5 and qualifier['Type'] in ['Analog', 'Digital'] and 0 <= qualifier['Red'] <= 255 \
                and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            ClockFontColorCmdString = 'set feature clock {index} {type}clockFont color: {fontColor}\r\n'.format(index=clock_idx-1,
                                                                                                  type=qualifier['Type'].lower(),
                                                                                                  fontColor=rgb_values)
            self.__SetHelper('ClockFontColor', ClockFontColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockFontColor')

    def SetClockNameFontColor(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])

        if 1 <= clock_idx <= 5 and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            ClockNameFontColorCmdString = 'set feature clock {index} clockNameFont color: {color}\r\n'.format(index=clock_idx-1, color=rgb_values)
            self.__SetHelper('ClockNameFontColor', ClockNameFontColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockNameFontColor')

    def SetClockNameTextCommand(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])
        clock_text = value

        if 1 <= clock_idx <= 5 and clock_text:
            if ' ' in clock_text:
                if clock_text[0] != '"' and clock_text[-1] != '"':
                    clock_text = '"{}"'.format(clock_text)
            ClockNameTextCommandCmdString = 'set feature clock {index} clockName: {text}\r\n'.format(index=clock_idx-1, text=clock_text)
            self.__SetHelper('ClockNameTextCommand', ClockNameTextCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockNameTextCommand')

    def SetClockTimezoneCommand(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])
        clock_timezone = value

        if 1 <= clock_idx <= 5 and clock_timezone:
            ClockTimezoneCommandCmdString = 'set feature clock {index} timeZone: {timeZone}\r\n'.format(index=clock_idx-1, timeZone=clock_timezone)
            self.__SetHelper('ClockTimezoneCommand', ClockTimezoneCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockTimezoneCommand')

    def SetClockVisible(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }

        clock_idx = int(qualifier['Clock'])

        if value in ValueStateValues and 1 <= clock_idx <= 5:
            ClockVisibleCmdString = 'set feature clock {index} visible: {visible}\r\n'.format(index=clock_idx-1, visible=ValueStateValues[value])
            self.__SetHelper('ClockVisible', ClockVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClockVisible')

    def UpdateClockVisible(self, value, qualifier):

        clock_idx = int(qualifier['Clock'])

        if 1 <= clock_idx <= 5:
            ClockVisibleCmdString = 'get feature clock {} visible\r\n'.format(clock_idx-1)
            self.__UpdateHelper('ClockVisible', ClockVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateClockVisible')

    def __MatchClockVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        qualifier = {'Clock' : str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ClockVisible', value, qualifier)

    def SetIconAnimationSpeed(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])
        state_idx = int(qualifier['State'])

        if 0 <= int(value) <= 10 and 1 <= icon_idx <= 5 and 0 <= state_idx <= 2:
            IconAnimationSpeedCmdString = 'set feature icon {index} animation {stateIndex} speed: {speed}\r\n'.format(index=icon_idx-1, stateIndex=state_idx, speed=value)
            self.__SetHelper('IconAnimationSpeed', IconAnimationSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconAnimationSpeed')

    def SetIconAnimationType(self, value, qualifier):

        ValueStateValues = {
            'Static': 'static',
            'Blink' : 'blink'
        }

        icon_idx = int(qualifier['Icon'])
        state_idx = int(qualifier['State'])

        if value in ValueStateValues and 1 <= icon_idx <= 5 and 0 <= state_idx <= 2:
            IconAnimationTypeCmdString = 'set feature icon {index} animation {stateIndex} type: {type}\r\n'.format(index=icon_idx-1, stateIndex=state_idx, type=ValueStateValues[value])
            self.__SetHelper('IconAnimationType', IconAnimationTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconAnimationType')

    def SetIconColor(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])
        state_idx = int(qualifier['State'])

        if 1 <= icon_idx <= 5 and 0 <= state_idx <= 2 and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            IconColorCmdString = 'set feature icon {index} color {stateIndex}: {color}\r\n'.format(index=icon_idx-1, stateIndex=state_idx, color=rgb_values)
            self.__SetHelper('IconColor', IconColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconColor')

    def SetIconFontColor(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])
        state_idx = int(qualifier['State'])

        if 1 <= icon_idx <= 5 and 0 <= state_idx <= 2 and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            IconFontColorCmdString = 'set feature icon {index} font {stateIndex} color: {color}\r\n'.format(index=icon_idx-1, stateIndex=state_idx, color=rgb_values)
            self.__SetHelper('IconFontColor', IconFontColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconFontColor')

    def SetIconRegion(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])

        if value in '01' and 1 <= icon_idx <= 5:
            IconRegionCmdString = 'set feature icon {index} region: {region}\r\n'.format(index=icon_idx-1, region=value)
            self.__SetHelper('IconRegion', IconRegionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconRegion')

    def SetIconState(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])

        if 0 <= int(value) <= 2 and 1 <= icon_idx <= 5:
            IconStateCmdString = 'set feature icon {index} state: {state}\r\n'.format(index=icon_idx-1, state=value)
            self.__SetHelper('IconState', IconStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconState')

    def SetIconTextCommand(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])
        state_idx = int(qualifier['State'])
        icon_text = value

        if 1 <= icon_idx <= 5 and 0 <= state_idx <= 2 and icon_text:
            if ' ' in icon_text:
                if icon_text[0] != '"' and icon_text[-1] != '"':
                    icon_text = '"{}"'.format(icon_text)
            IconTextCommandCmdString = 'set feature icon {index} text {stateIndex}: {text}\r\n'.format(index=icon_idx-1, stateIndex=state_idx, text=icon_text)
            self.__SetHelper('IconTextCommand', IconTextCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconTextCommand')

    def SetIconVisible(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }

        icon_idx = int(qualifier['Icon'])

        if value in ValueStateValues and 1 <= icon_idx <= 5:
            IconVisibleCmdString = 'set feature icon {index} visible: {visible}\r\n'.format(index=icon_idx-1, visible=ValueStateValues[value])
            self.__SetHelper('IconVisible', IconVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIconVisible')

    def UpdateIconVisible(self, value, qualifier):

        icon_idx = int(qualifier['Icon'])

        if 1 <= icon_idx <= 5:
            IconVisibleCmdString = 'get feature icon {} visible\r\n'.format(icon_idx-1)
            self.__UpdateHelper('IconVisible', IconVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateIconVisible')

    def __MatchIconVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        qualifier = {'Icon' : str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('IconVisible', value, qualifier)

    def SetLayoutConfiguration(self, value, qualifier):

        if value in '01234':
            LayoutConfigurationCmdString = 'set feature layout id: {id}\r\n'.format(id=value)
            self.__SetHelper('LayoutConfiguration', LayoutConfigurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayoutConfiguration')

    def UpdateLayoutConfiguration(self, value, qualifier):

        LayoutConfigurationCmdString = 'get feature layout id\r\n'
        self.__UpdateHelper('LayoutConfiguration', LayoutConfigurationCmdString, value, qualifier)

    def __MatchLayoutConfiguration(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('LayoutConfiguration', value, None)

    def SetLogoVisible(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'true',
            'Off' : 'false'
        }

        logo_idx = int(qualifier['Logo'])

        if 1 <= logo_idx <= 2 and value in ValueStateValues:
            LogoVisibleCmdString = 'set feature logo {index} visible: {visible}\r\n'.format(index=logo_idx-1, visible=ValueStateValues[value])
            self.__SetHelper('LogoVisible', LogoVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoVisible')

    def UpdateLogoVisible(self, value, qualifier):

        logo_idx = int(qualifier['Logo'])

        if 1 <= logo_idx <= 2:
            LogoVisibleCmdString = 'get feature logo {index} visible\r\n'.format(index=logo_idx-1)
            self.__UpdateHelper('LogoVisible', LogoVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoVisible')

    def __MatchLogoVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        qualifier = {'Logo' :str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LogoVisible', value, qualifier)

    def SetMessageAnimationSpeed(self, value, qualifier):

        message_idx = int(qualifier['Message'])

        if 0 <= int(value) <= 10 and 1 <= message_idx <= 3:
            MessageAnimationSpeedCmdString = 'set feature message {index} animation speed: {speed}\r\n'.format(index=message_idx-1, speed=value)
            self.__SetHelper('MessageAnimationSpeed', MessageAnimationSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageAnimationSpeed')

    def SetMessageAnimationType(self, value, qualifier):

        ValueStateValues = {
            'Static': 'static',
            'Blink' : 'blink'
        }

        message_idx = int(qualifier['Message'])

        if value in ValueStateValues and 1 <= message_idx <= 3:
            MessageAnimationTypeCmdString = 'set feature message {index} animation type: {type}\r\n'.format(index=message_idx-1, type=ValueStateValues[value])
            self.__SetHelper('MessageAnimationType', MessageAnimationTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageAnimationType')

    def SetMessageFontColor(self, value, qualifier):

        message_idx = int(qualifier['Message'])

        if 1 <= message_idx <= 3 and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            rgb_values = '#{red:02x}{green:02x}{blue:02x}'.format(red=qualifier['Red'],
                                                                  green=qualifier['Green'],
                                                                  blue=qualifier['Blue'])
            MessageFontColorCmdString = 'set feature message {index} font color: {color}\r\n'.format(index=message_idx-1, color=rgb_values)
            self.__SetHelper('MessageFontColor', MessageFontColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageFontColor')

    def SetMessageFontSize(self, value, qualifier):

        message_idx = int(qualifier['Message'])

        if 1 <= message_idx <= 3 and 0 <= int(value) <= 255:
            MessageFontSizeCmdString = 'set feature message {index} font size: {size}\r\n'.format(index=message_idx-1, size=value)
            self.__SetHelper('MessageFontSize', MessageFontSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageFontSize')

    def SetMessageTextCommand(self, value, qualifier):

        message_idx = int(qualifier['Message'])
        message_text = value

        if 1 <= message_idx <= 3 and message_text:
            if ' ' in message_text:
                if message_text[0] != '"' and message_text[-1] != '"':
                    message_text = '"{}"'.format(message_text)
            MessageTextCommandCmdString = 'set feature message {index} text: {text}\r\n'.format(index=message_idx-1, text=message_text)
            self.__SetHelper('MessageTextCommand', MessageTextCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageTextCommand')

    def SetMessageVisible(self, value, qualifier):

        ValueStateValues = {
            'On' : 'true',
            'Off': 'false'
        }

        message_idx = int(qualifier['Message'])

        if value in ValueStateValues and 1 <= message_idx <= 3:
            MessageVisibleCmdString = 'set feature message {index} visible: {visible}\r\n'.format(index=message_idx-1, visible=ValueStateValues[value])
            self.__SetHelper('MessageVisible', MessageVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMessageVisible')

    def UpdateMessageVisible(self, value, qualifier):

        message_idx = int(qualifier['Message'])

        if 1 <= message_idx <= 3:
            MessageVisibleCmdString = 'get feature message {} visible\r\n'.format(message_idx-1)
            self.__UpdateHelper('MessageVisible', MessageVisibleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMessageVisible')

    def __MatchMessageVisible(self, match, tag):

        ValueStateValues = {
            'true'  : 'On',
            'false' : 'Off',
        }

        qualifier = {'Message' : str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MessageVisible', value, qualifier)

    def SetPresetRecallCommand(self, value, qualifier):

        preset_text = value
        if preset_text:
            if ' ' in preset_text:
                if preset_text[0] != '"' and preset_text[-1] != '"':
                    preset_text = '"{}"'.format(preset_text)

            PresetRecallCommandCmdString = 'set setup runpreset: {}\r\n'.format(preset_text)
            self.__SetHelper('PresetRecallCommand', PresetRecallCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallCommand')

    def SetSetupDatetimeCommand(self, value, qualifier):

        TypeStates = {
            'Date & Time' : 'time',
            'NTP'         : 'ntp 0'
        }

        datetime_text = value

        if qualifier['Type'] in TypeStates and datetime_text:
            SetupDatetimeCommandCmdString = 'set setup datetime {type}: {date}\r\n'.format(type=TypeStates[qualifier['Type']], date=datetime_text)
            self.__SetHelper('SetupDatetimeCommand', SetupDatetimeCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetupDatetimeCommand')

    def UpdateSetupDatetimeStatus(self, value, qualifier):

        TypeStates = {
            'Date & Time' : 'time',
            'NTP'         : 'ntp 0'
        }

        if qualifier['Type'] in TypeStates:
            SetupDatetimeStatusCmdString = 'get setup datetime {type}\r\n'.format(type=TypeStates[qualifier['Type']])
            self.__UpdateHelper('SetupDatetimeStatus', SetupDatetimeStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSetupDatetimeStatus')

    def __MatchSetupDatetimeStatus(self, match, tag):

        value = match.group(1).decode()
        if tag == 'Time':
            self.WriteStatus('SetupDatetimeStatus', value, {'Type': 'Date & Time'})
        else:
            self.WriteStatus('SetupDatetimeStatus', value, {'Type': 'NTP'})

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated == 'Not Needed':
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                    
                self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.counter = 0

        self.Error(['Error: {}'.format(match.group(0).decode())])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'Needed'

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

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return 
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning') 

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)

        if platform == 'Pro' and version < minimumVersion:
            self.Error(['Minimum API version not met. Needs to be >= 3.4.6'])
        else:
            EthernetClientInterface.SSLWrap(self, certificate=None, cert_reqs='CERT_NONE', ssl_version='TLSv2', ca_certs= None)

        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()