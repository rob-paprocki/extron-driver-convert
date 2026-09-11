from Extron2.HTTPDriver import HTTPDriver
from extronlib.system import ProgramLog
import urllib.error
import urllib.request
import base64
import re

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)

        if deviceUsername and devicePassword:
            authentication = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            authentication.add_password(None, self.RootURL, deviceUsername, devicePassword)
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler(authentication))
        else:
            self.Opener = urllib.request.build_opener(urllib.request.HTTPDigestAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Applications': {'Status': {}},
            'ChromaKeylessOverlapReset': {'Status': {}},
            'CloseupDetectionArea': {'Parameters': ['X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4'], 'Status': {}},
            'CloseupDetectionSize': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Parameters': ['Width of Preview Image', 'Height of Preview Image',
                                                        'Width of Minimum Size', 'Height of Minimum Size', 'Width of Maximum Size', 'Height of Maximum Size'], 'Status': {}},
            'CloseupSensitivity': {'Status': {}},
            'CloseupTimeOut': {'Status': {}},
            'CropFramePosition': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Parameters': ['Width of Whole Image', 'Height of Whole Image',
                                                       'Upper Left X of Crop Area', 'Upper Left Y of Crop Area', 'Width of Crop Area', 'Height of Crop Area'], 'Status': {}},
            'HandwritingExtractArea': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Parameters': ['Width of Preview Image', 'Height of Preview Image',
                                                       'Upper Left X of Target Area', 'Upper Left Y of Target Area', 'Upper Right X of Target Area', 'Upper Right Y of Target Area',
                                                       'Bottom Left X of Target Area', 'Bottom Left Y of Target Area', 'Bottom Right X of Target Area', 'Bottom Right Y of Target Area'], 'Status': {}},
            'HandwritingExtractBoardColor': {'Status': {}},
            'HandwritingExtractMargin': {'Status': {}},
            'HandwritingExtractOverlapMode': {'Status': {}},
            'HandwritingExtractOverlapTransparency': {'Status': {}},
            'HandwritingExtractTextColor': {'Status': {}},
            'Power': {'Status': {}},
            'PTZControl': {'Status': {}},
            'PTZTrackingMode': {'Status': {}},
            'PTZTrackingResetCamera': {'Status': {}},
            'PTZTrackingSensitivity': {'Status': {}},
            'PTZTrackingShotMode': {'Status': {}},
            'PTZTrackingTriggerType': {'Status': {}},
            'SaveApplication': {'Parameters': ['Applications'], 'Status': {}},
            'SetupApplication': {'Parameters': ['Applications'], 'Status': {}},
            'SoftwareVersion': {'Status': {}},
        }

        self.SoftwareRegex = re.compile('SoftVersion=\"([A-Za-z0-9.]{8})\"')
        self.AppsRegex = re.compile('CurrentApp=(set)?entry,(crop|ptztracking|handwextract|closeup|config|initial_setup|chromakey-less|standby)')
        self.PTZRegex = re.compile('PtzTrackingTriggerType=(set)?(auto|manual)')

    def SetApplications(self, value, qualifier):

        ValueStateValues = {
            'Real-time Cropping': 'crop',
            'PTZ Auto Tracking': 'ptztracking',
            'Handwriting Extraction': 'handwextract',
            'Close-up by Gesture': 'closeup',
            'Common Setting': 'config',
            'Chroma key-less CG Overlay': 'chromakey-less',
            'Standby': 'standby',
        }

        if value in ValueStateValues:
            ApplicationsCmdString = '/analytics/analyticsbox.cgi?AppControl=entry,{}'.format(ValueStateValues[value])
            self.__SetHelper('Applications', value, qualifier, ApplicationsCmdString)
        else:
            self.Discard('Invalid Command for SetApplications')

    def UpdateApplications(self, value, qualifier):

        ValueStateValues = {
            'crop': 'Real-time Cropping',
            'ptztracking': 'PTZ Auto Tracking',
            'handwextract': 'Handwriting Extraction',
            'closeup': 'Close-up by Gesture',
            'config': 'Common Setting',
            'initial_setup': 'Initial Setup',
            'chromakey-less': 'Chroma key-less CG Overlay',
            'standby': 'Standby',
        }

        ApplicationsCmdString = '/analytics/inquiry.cgi?inq=analyticsbox'
        res = self.__UpdateHelper('Applications', value, qualifier, ApplicationsCmdString)
        if res:
            try:
                Temp = re.search(self.AppsRegex, res)
                value = ValueStateValues[Temp.group(2)]
                self.WriteStatus('Applications', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Applications: Invalid/unexpected response'])

    def SetChromaKeylessOverlapReset(self, value, qualifier):

        ChromaKeylessOverlapResetCmdString = '/analytics/chromakey-less.cgi?ChromaKeyLessOverlapReset=On'
        self.__SetHelper('ChromaKeylessOverlapReset', value, qualifier, ChromaKeylessOverlapResetCmdString)

    def SetCloseupDetectionArea(self, value, qualifier):

        XConstraints = {
            'Min': -320,
            'Max': 960,
        }

        YConstraints = {
            'Min': -180,
            'Max': 540,
        }

        x1 = qualifier['X1']
        y1 = qualifier['Y1']
        x2 = qualifier['X2']
        y2 = qualifier['Y2']
        x3 = qualifier['X3']
        y3 = qualifier['Y3']
        x4 = qualifier['X4']
        y4 = qualifier['Y4']

        if (XConstraints['Min'] <= x1 <= XConstraints['Max'] and XConstraints['Min'] <= x2 <= XConstraints['Max']
                and XConstraints['Min'] <= x3 <= XConstraints['Max'] and XConstraints['Min'] <= x4 <= XConstraints['Max']
                and YConstraints['Min'] <= y1 <= YConstraints['Max'] and YConstraints['Min'] <= y2 <= YConstraints['Max']
                and YConstraints['Min'] <= y3 <= YConstraints['Max'] and YConstraints['Min'] <= y4 <= YConstraints['Max']):
            CloseupDetectionAreaCmdString = '/analytics/closeup.cgi?DetectionArea={},{},{},{},{},{},{},{}'.format(x1, y1, x2, y2, x3, y3, x4, y4)
            self.__SetHelper('CloseupDetectionArea', value, qualifier, CloseupDetectionAreaCmdString)
        else:
            self.Discard('Invalid Command for SetCloseupDetectionArea')

    def SetCloseupDetectionSize(self, value, qualifier):

        WidthConstraints = {
            'Min': 0,
            'Max': 3840,
        }

        HeightConstraints = {
            'Min': 0,
            'Max': 2160,
        }

        PIWidth = qualifier['Width of Preview Image']
        PIHeight = qualifier['Height of Preview Image']
        MinWidth = qualifier['Width of Minimum Size']
        MinHeight = qualifier['Height of Minimum Size']
        MaxWidth = qualifier['Width of Maximum Size']
        MaxHeight = qualifier['Height of Maximum Size']

        if (WidthConstraints['Min'] <= PIWidth <= WidthConstraints['Max'] and HeightConstraints['Min'] <= PIHeight <= HeightConstraints['Max']
                and WidthConstraints['Min'] <= MinWidth <= WidthConstraints['Max'] and HeightConstraints['Min'] <= MinHeight <= HeightConstraints['Max']
                and WidthConstraints['Min'] <= MaxWidth <= WidthConstraints['Max'] and HeightConstraints['Min'] <= MaxHeight <= HeightConstraints['Max']):
            CloseupDetectionSizeCmdString = '/analytics/closeup.cgi?DetectionSize={},{},{},{},{},{}'.format(PIWidth, PIHeight, MinWidth, MinHeight, MaxWidth, MaxHeight)
            self.__SetHelper('CloseupDetectionSize', value, qualifier, CloseupDetectionSizeCmdString)
        else:
            self.Discard('Invalid Command for SetCloseupDetectionSize')

    def SetCloseupSensitivity(self, value, qualifier):

        ValueStateValues = {
            'High': 'High',
            'Mid': 'Mid',
            'Low': 'Low',
        }

        if value in ValueStateValues:
            CloseupSensitivityCmdString = '/analytics/closeup.cgi?CloseupSensitivity={}'.format(ValueStateValues[value])
            self.__SetHelper('CloseupSensitivity', value, qualifier, CloseupSensitivityCmdString)
        else:
            self.Discard('Invalid Command for SetCloseupSensitivity')

    def SetCloseupTimeOut(self, value, qualifier):

        if 1 <= value <= 600:
            CloseupTimeOutCmdString = '/analytics/closeup.cgi?CloseupTimeoutSec={}'.format(value)
            self.__SetHelper('CloseupTimeOut', value, qualifier, CloseupTimeOutCmdString)
        else:
            self.Discard('Invalid Command for SetCloseupTimeOut')

    def SetCropFramePosition(self, value, qualifier):

        WIWidthConstraints = {
            'Min': 0,
            'Max': 3840,
        }

        WIHeightConstraints = {
            'Min': 0,
            'Max': 2160,
        }

        ULXCAConstraints = {
            'Min': 0,
            'Max': 3839,
        }

        ULYCAConstraints = {
            'Min': 0,
            'Max': 2159,
        }

        CAWidthConstraints = {
            'Min': 0,
            'Max': 3840,
        }

        CAHeightConstraints = {
            'Min': 0,
            'Max': 2160,
        }

        WIWidth = qualifier['Width of Whole Image']
        WIHeight = qualifier['Height of Whole Image']
        ULXCrA = qualifier['Upper Left X of Crop Area']
        ULYCrA = qualifier['Upper Left Y of Crop Area']
        CAWidth = qualifier['Width of Crop Area']
        CAHeight = qualifier['Height of Crop Area']
        if (WIWidthConstraints['Min'] <= WIWidth <= WIWidthConstraints['Max'] and WIHeightConstraints['Min'] <= WIHeight <= WIHeightConstraints['Max']
                and CAWidthConstraints['Min'] <= CAWidth <= CAWidthConstraints['Max'] and CAHeightConstraints['Min'] <= CAHeight <= CAHeightConstraints['Max']
                and ULXCAConstraints['Min'] <= ULXCrA <= ULXCAConstraints['Max'] and ULYCAConstraints['Min'] <= ULYCrA <= ULYCAConstraints['Max']):
            CropFramePositionCmdString = '/analytics/crop.cgi?CropFramePosition={},{},{},{},{},{}'.format(WIWidth, WIHeight, ULXCrA, ULYCrA, CAWidth, CAHeight)
            self.__SetHelper('CropFramePosition', value, qualifier, CropFramePositionCmdString)
        else:
            self.Discard('Invalid Command for SetCropFramePosition')

    def SetHandwritingExtractArea(self, value, qualifier):

        PIWidthConstraints = {
            'Min': 0,
            'Max': 640,
        }

        PIHeightConstraints = {
            'Min': 0,
            'Max': 360,
        }

        XTAConstraints = {
            'Min': 0,
            'Max': 639,
        }

        YTAConstraints = {
            'Min': 0,
            'Max': 359,
        }

        PIWidth = qualifier['Width of Preview Image']
        PIHeight = qualifier['Height of Preview Image']
        ULXTaA = qualifier['Upper Left X of Target Area']
        ULYTaA = qualifier['Upper Left Y of Target Area']
        URXTaA = qualifier['Upper Right X of Target Area']
        URYTaA = qualifier['Upper Right Y of Target Area']
        BLXTaA = qualifier['Bottom Left X of Target Area']
        BLYTaA = qualifier['Bottom Left Y of Target Area']
        BRXTaA = qualifier['Bottom Right X of Target Area']
        BRYTaA = qualifier['Bottom Right Y of Target Area']
        if (PIWidthConstraints['Min'] <= PIWidth <= PIWidthConstraints['Max'] and PIHeightConstraints['Min'] <= PIHeight <= PIHeightConstraints['Max']
                and XTAConstraints['Min'] <= ULXTaA <= XTAConstraints['Max'] and YTAConstraints['Min'] <= ULYTaA <= YTAConstraints['Max']
                and XTAConstraints['Min'] <= URXTaA <= XTAConstraints['Max'] and YTAConstraints['Min'] <= URYTaA <= YTAConstraints['Max']
                and XTAConstraints['Min'] <= BLXTaA <= XTAConstraints['Max'] and YTAConstraints['Min'] <= BLYTaA <= YTAConstraints['Max']
                and XTAConstraints['Min'] <= BRXTaA <= XTAConstraints['Max'] and YTAConstraints['Min'] <= BRYTaA <= YTAConstraints['Max']):
            HandwritingExtractAreaCmdString = '/analytics/handwextract.cgi?HandwExtractArea={},{},{},{},{},{},{},{},{},{}'.format(PIWidth, PIHeight,
                                                                                                                                  ULXTaA, ULYTaA, URXTaA, URYTaA, BLXTaA, BLYTaA, BRXTaA, BRYTaA)
            self.__SetHelper('HandwritingExtractArea', value, qualifier, HandwritingExtractAreaCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractArea')

    def SetHandwritingExtractBoardColor(self, value, qualifier):

        ValueStateValues = {
            'White': 'white',
            'Black': 'black',
        }

        if value in ValueStateValues:
            HandwritingExtractBoardColorCmdString = '/analytics/handwextract.cgi?HandwExtractBoardColor={}'.format(ValueStateValues[value])
            self.__SetHelper('HandwritingExtractBoardColor', value, qualifier, HandwritingExtractBoardColorCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractBoardColor')

    def SetHandwritingExtractMargin(self, value, qualifier):

        if 0 <= value <= 100:
            HandwritingExtractMarginCmdString = '/analytics/handwextract.cgi?HandwExtractMargin={}'.format(value)
            self.__SetHelper('HandwritingExtractMargin', value, qualifier, HandwritingExtractMarginCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractMargin')

    def SetHandwritingExtractOverlapMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
        }

        if value in ValueStateValues:
            HandwritingExtractOverlapModeCmdString = '/analytics/handwextract.cgi?HandwExtractOverlapMode={}'.format(ValueStateValues[value])
            self.__SetHelper('HandwritingExtractOverlapMode', value, qualifier, HandwritingExtractOverlapModeCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractOverlapMode')

    def SetHandwritingExtractOverlapTransparency(self, value, qualifier):

        if 0 <= value <= 100:
            HandwritingExtractOverlapTransparencyCmdString = '/analytics/handwextract.cgi?HandwExtractOverlapTransparency={}'.format(value)
            self.__SetHelper('HandwritingExtractOverlapTransparency', value, qualifier, HandwritingExtractOverlapTransparencyCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractOverlapTransparency')

    def SetHandwritingExtractTextColor(self, value, qualifier):

        ValueStateValues = {
            'Color': 'color',
            'Black': 'black',
        }

        if value in ValueStateValues:
            HandwritingExtractTextColorCmdString = '/analytics/handwextract.cgi?HandwExtractTextColor={}'.format(ValueStateValues[value])
            self.__SetHelper('HandwritingExtractTextColor', value, qualifier, HandwritingExtractTextColorCmdString)
        else:
            self.Discard('Invalid Command for SetHandwritingExtractTextColor')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Standby': 'off',
        }

        if value in ValueStateValues:
            PowerCmdString = '/analytics/analyticsbox.cgi?Active={}'.format(ValueStateValues[value])
            self.__SetHelper('Power', value, qualifier, PowerCmdString)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPTZControl(self, value, qualifier):

        ValueStateValues = {
            'Left': 'Move=left,pantilt',
            'Right': 'Move=right,pantilt',
            'Up': 'Move=up,pantilt',
            'Down': 'Move=down,pantilt',
            'Up Left': 'Move=up-left,pantilt',
            'Up Right': 'Move=up-right,pantilt',
            'Down Left': 'Move=down-left,pantilt',
            'Down Right': 'Move=down-right,pantilt',
            'Tele': 'Move=tele,zoom',
            'Wide': 'Move=wide,zoom',
            'Stop Pan Tilt': 'Move=stop,pantilt',
            'Stop Zoom': 'Move=stop,zoom',
        }

        if value in ValueStateValues:
            PTZControlCmdString = '/command/ptzf.cgi?{}'.format(ValueStateValues[value])
            self.__SetHelper('PTZControl', value, qualifier, PTZControlCmdString)
        else:
            self.Discard('Invalid Command for SetPTZControl')

    def SetPTZTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Free Object Pan': 'leftright',
            'Fixed Frame Pan': 'handwrite',
        }

        if value in ValueStateValues:
            PTZTrackingModeCmdString = '/analytics/ptztracking.cgi?PtzTrackingMode={}'.format(ValueStateValues[value])
            self.__SetHelper('PTZTrackingMode', value, qualifier, PTZTrackingModeCmdString)
        else:
            self.Discard('Invalid Command for SetPTZTrackingMode')

    def SetPTZTrackingResetCamera(self, value, qualifier):

        PTZTrackingResetCameraCmdString = '/analytics/ptztracking.cgi?PtzTrackingResetCamera=On'
        self.__SetHelper('PTZTrackingResetCamera', value, qualifier, PTZTrackingResetCameraCmdString)

    def SetPTZTrackingSensitivity(self, value, qualifier):

        ValueStateValues = {
            'Normal': 'normal',
            'High': 'high',
        }

        if value in ValueStateValues:
            PTZTrackingSensitivityCmdString = '/analytics/ptztracking.cgi?PtzTrackingSensitivity={}'.format(ValueStateValues[value])
            self.__SetHelper('PTZTrackingSensitivity', value, qualifier, PTZTrackingSensitivityCmdString)
        else:
            self.Discard('Invalid Command for SetPTZTrackingSensitivity')

    def SetPTZTrackingShotMode(self, value, qualifier):

        ValueStateValues = {
            'Full Body': 'fullshot',
            'Upper Body': 'bustshot',
        }

        if value in ValueStateValues:
            PTZTrackingShotModeCmdString = '/analytics/ptztracking.cgi?PtzTrackingShotModeLR={}'.format(ValueStateValues[value])
            self.__SetHelper('PTZTrackingShotMode', value, qualifier, PTZTrackingShotModeCmdString)
        else:
            self.Discard('Invalid Command for SetPTZTrackingShotMode')

    def SetPTZTrackingTriggerType(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            'Manual': 'manual',
        }

        if value in ValueStateValues:
            PTZTrackingTriggerTypeCmdString = '/analytics/ptztracking.cgi?PtzTrackingTriggerType={}'.format(ValueStateValues[value])
            self.__SetHelper('PTZTrackingTriggerType', value, qualifier, PTZTrackingTriggerTypeCmdString)
        else:
            self.Discard('Invalid Command for SetPTZTrackingTriggerType')

    def UpdatePTZTrackingTriggerType(self, value, qualifier):

        ValueStateValues = {
            'auto': 'Auto',
            'manual': 'Manual',
        }

        PTZTrackingTriggerTypeCmdString = '/analytics/inquiry.cgi?inq=ptztracking'
        res = self.__UpdateHelper('PTZTrackingTriggerType', value, qualifier, PTZTrackingTriggerTypeCmdString)
        if res:
            try:
                temp = re.search(self.PTZRegex, res)
                value = ValueStateValues[temp.group(2)]
                self.WriteStatus('PTZTrackingTriggerType', value, qualifier)
            except (KeyError, IndexError, AttributeError):
                self.Error(['PTZ Tracking Trigger Type: Invalid/unexpected response'])

    def SetSaveApplication(self, value, qualifier):

        ApplicationsStates = {
            'Real-time Cropping': 'crop',
            'PTZ Auto Tracking': 'ptztracking',
            'Handwriting Extraction': 'handwextract',
            'Close-up by Gesture': 'closeup',
            'Common Setting': 'config',
            'Initial Setup': 'initial_setup',
            'Chroma key-less CG Overlay': 'chromakey-less',
            'Standby': 'standby',
        }

        apps = qualifier['Applications']
        if apps in ApplicationsStates:
            SaveApplicationCmdString = '/analytics/analyticsbox.cgi?AppConfigSetup=save,{}'.format(ApplicationsStates[apps])
            self.__SetHelper('SaveApplication', value, qualifier, SaveApplicationCmdString)
        else:
            self.Discard('Invalid Command for SetSaveApplication')

    def SetSetupApplication(self, value, qualifier):

        ApplicationsStates = {
            'Real-time Cropping': 'crop',
            'PTZ Auto Tracking': 'ptztracking',
            'Handwriting Extraction': 'handwextract',
            'Close-up by Gesture': 'closeup',
            'Common Setting': 'config',
            'Chroma key-less CG Overlay': 'chromakey-less',
            'Standby': 'standby',
        }

        apps = qualifier['Applications']
        if apps in ApplicationsStates:
            SetupApplicationCmdString = '/analytics/analyticsbox.cgi?AppControl=setentry,{}'.format(ApplicationsStates[apps])
            self.__SetHelper('SetupApplication', value, qualifier, SetupApplicationCmdString)
        else:
            self.Discard('Invalid Command for SetSetupApplication')

    def UpdateSoftwareVersion(self, value, qualifier):

        SoftwareVersionCmdString = '/command/inquiry.cgi?inqjs=system'
        res = self.__UpdateHelper('SoftwareVersion', value, qualifier, SoftwareVersionCmdString)
        if res:
            try:
                value = re.search(self.SoftwareRegex, res).group(1)
                self.WriteStatus('SoftwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Software Version: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):
        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url, data=None):
        self.Debug = True

        ipadd = re.search(r'http://(\S+):[0-9]+/', self.RootURL)
        url = 'http://{0}{1}'.format(ipadd.group(1), url)

        headers = {
            'Content-Type': 'text/html',
            'Referer': 'http://{}/setup/system?lang=en'.format(ipadd.group(1))
          }
        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url, data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        ipadd = re.search(r'http://(\S+):[0-9]+/', self.RootURL)
        url = 'http://{0}{1}'.format(ipadd.group(1), url)

        headers = {
            'Content-Type': 'text/html',
            'Referer': 'http://{}/setup/system?lang=en'.format(ipadd.group(1))
          }

        my_request = urllib.request.Request(url, data=data, headers=headers, method='GET')

        try:
            res = self.Opener.open(my_request, timeout=10)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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

class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])