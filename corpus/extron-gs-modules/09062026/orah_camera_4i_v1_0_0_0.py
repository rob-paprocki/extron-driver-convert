import base64
import urllib.error
import urllib.request
import json


class DeviceClass:

    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AudioSource': {'Status': {}},
            'StartBroadcasting': {'Parameters': ['Preset'], 'Status': {}},
            'StartRecording': {'Parameters': ['Output Preset Drive Path'], 'Status': {}},
            'StopBroadcasting': {'Status': {}},
            'StopRecording': {'Status': {}},
        }

    def SetAudioSource(self, value, qualifier):

        ValueStateValues = {
            'Camera (Stereo)': ["camera", "stereo"],
            'Camera (Ambisonic)': ["camera", "amb_wxyz"],
            'Line In (Stereo)': ["line-in", "stereo"]
        }

        CmdString = {"name": "audio.set_source", "parameters": {"source": ValueStateValues[value][0], "layout": ValueStateValues[value][1]}}
        self.__SetHelper('AudioSource', value, qualifier, url='', data=CmdString)

    def SetStartBroadcasting(self, value, qualifier):

        CmdString = {"name": "stitcher.start_stream", "parameters": {"preset": qualifier['Preset']}}
        self.__SetHelper('StartBroadcasting', value, qualifier, url='', data=CmdString)

    def SetStartRecording(self, value, qualifier):

        CmdString = {"name": "stitcher.start_recording", "parameters": {"output_preset": {"drive_path": qualifier['Output Preset Drive Path']}}}
        self.__SetHelper('StartRecording', value, qualifier, url='', data=CmdString)

    def SetStopBroadcasting(self, value, qualifier):

        CmdString = {"name": "stitcher.stop_stream"}
        self.__SetHelper('StopBroadcasting', value, qualifier, url='', data=CmdString)

    def SetStopRecording(self, value, qualifier):

        CmdString = {"name": "stitcher.stop_recording"}
        self.__SetHelper('StopRecording', value, qualifier, url='', data=CmdString)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        res = response.read().decode()
        return res

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{0}/commands/execute'.format(self.RootURL.rstrip('/'))
        data = json.dumps(data).encode()
        headers = {'Content-Type': 'application/json'}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request)
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
