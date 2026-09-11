from extronlib.system import ProgramLog, Wait
import base64
import urllib.error
import urllib.request
from json import loads, dumps

class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword):
        
        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler()) 

        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port
        self.deviceUsername = deviceUsername
        self.devicePassword = devicePassword
        self.Models = {}

        self.Commands = {
            'JoinDisplayAudio': {'Parameters':['Source ID','Display ID','Mute','Volume'], 'Status': {}},
            'JoinDisplayVideo': {'Parameters':['Source ID','Display ID','Position','Cropping'], 'Status': {}},
            'Layout': {'Parameters':['ID/Name','Source ID'], 'Status': {}},
            'Preset': {'Parameters':['ID/Name'], 'Status': {}},
            'UnjoinActiveDisplay': {'Parameters':['Source ID','Display ID'], 'Status': {}},
            'UnjoinSurface': {'Parameters':['ID'], 'Status': {}},
        }
        
        self.access_token = ''
        self._headers = {'Content-Type': 'application/json'}

    def SetLogin(self, value, qualifier):

        url = 'v4/authenticate?username={}&password={}'.format(self.deviceUsername, self.devicePassword)
        res = self.__SetHelper('Login', value, qualifier, url=url, data=None, method='POST')
        if res:
            try:
                self.access_token = res['payload']['token']
            except:
                self.Error(['Login: Invalid/unexpected response'])
        else:
            self.Error(['Login Failed'])

    def SetJoinDisplayAudio(self, value, qualifier):

        MuteStates = {
            'On':  True, 
            'Off': False
        }

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if self.access_token :
            src_id = qualifier['Source ID']
            display_id = qualifier['Display ID']
            mute_val = qualifier['Mute']
            vol_val = qualifier['Volume']
            if (src_id and display_id and mute_val in MuteStates and 
                VolumeConstraints['Min'] <= vol_val <= VolumeConstraints['Max']):
                url = 'v4/joins'
                data = dumps([{
                              "sourceId": src_id,
                              "displayId": display_id,
                              "parameters":{
                                    "type" : "Audio",
                                    "muted": MuteStates[mute_val],
                                    "volume": vol_val
                                    }
                            }]) 
                self.__SetHelper('JoinDisplayAudio', value, qualifier, url=url, data=data.encode('iso-8859-1'), method='POST')
            else:
                self.Discard('Invalid Command for SetJoinDisplayAudio')
        else:
            self.SetLogin(None, None)

    def SetJoinDisplayVideo(self, value, qualifier):

        if self.access_token :
            src_id = qualifier['Source ID']
            display_id = qualifier['Display ID']
            pos_val = qualifier['Position']
            crop_val = qualifier['Cropping']
            if src_id and display_id and pos_val and crop_val:
                ind_pos = pos_val.split(',')
                ind_crop = crop_val.split(',')
                if len(ind_pos) == 4 and len(ind_crop) == 4:
                    url = 'v4/joins'
                    data = dumps([{
                                  "sourceId": src_id,
                                  "displayId": display_id,
                                  "parameters":{
                                        "type" : "Video",
                                        "position": {
                                            "left": float(ind_pos[0]),
                                            "right": float(ind_pos[1]),
                                            "top": float(ind_pos[2]),
                                            "bottom": float(ind_pos[3])
                                            },
                                        "cropping": {
                                            "left": float(ind_crop[0]),
                                            "right": float(ind_crop[1]),
                                            "top": float(ind_crop[2]),
                                            "bottom": float(ind_crop[3])
                                            }
                                        }
                                }])
                    self.__SetHelper('JoinDisplayVideo', value, qualifier, url=url, data=data.encode('iso-8859-1'), method='POST')
                else:
                    self.Discard('Invalid Command for SetJoinDisplayVideo')
            else:
                self.Discard('Invalid Command for SetJoinDisplayVideo')
        else:
            self.SetLogin(None, None)

    def SetLayout(self, value, qualifier):

        if self.access_token :
            id_val = qualifier['ID/Name']
            src_id = qualifier['Source ID']
            if id_val and src_id:
                url = 'v4/layouts/apply'
                data = dumps({
                              "displayId": src_id,
                              "layoutId": id_val
                            })  
                self.__SetHelper('Layout', value, qualifier, url=url, data=data.encode('iso-8859-1'), method='POST')
            else:
                self.Discard('Invalid Command for SetLayout')
        else:
            self.SetLogin(None, None)

    def SetPreset(self, value, qualifier):

        if self.access_token :
            id_val = qualifier['ID/Name']
            if id_val:
                url = 'v4/presets/apply?presetId={}'.format(id_val.replace(' ','%20'))
                self.__SetHelper('Preset', value, qualifier, url=url, data=None, method='POST')
            else:
                self.Discard('Invalid Command for SetPreset')
        else:
            self.SetLogin(None, None)

    def SetUnjoinActiveDisplay(self, value, qualifier):

        if self.access_token :
            src_id = qualifier['Source ID']
            display_id = qualifier['Display ID']
            unjoin_id = ''
            url = 'v4/joins'
            res = self.__SetHelper('UnjoinActiveDisplay', value, qualifier, url=url, data=None, method='GET')
            try:
                payload_dict = res["payload"]
                dict1 = {}
                for i in payload_dict:
                    dict1[''.join([str(i["sourceId"]), str(i["displayId"])])] = i["id"] 
                id_val = ''.join([src_id, display_id ])
                for val in dict1:
                    if val == id_val:
                        unjoin_id = dict1[id_val]
                        break
            except:
                self.Error(['Invalid response for Active Display List'])
            else:
                if unjoin_id :
                    url = 'v4/joins/{}'.format(unjoin_id.replace(' ','%20'))
                    self.__SetHelper('UnjoinActiveDisplay', value, qualifier, url=url, data=None, method='DELETE')
                else:
                    self.Discard('Invalid Command for SetUnjoinActiveDisplay')
        else:
            self.SetLogin(None, None)

    def SetUnjoinSurface(self, value, qualifier):

        if self.access_token :
            id_val = qualifier['ID']
            if id_val:
                url = 'v4/joins?displayIds={}'.format(id_val.replace(' ','%20'))
                self.__SetHelper('UnjoinSurface', value, qualifier, url=url, data=None, method='DELETE')
            else:
                self.Discard('Invalid Command for SetUnjoinSurface')
        else:
            self.SetLogin(None, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            return loads(response.read().decode('iso-8859-1'))
        except:
            return ''

    def __SetHelper(self, command, value, qualifier, url, data, method):

        self.Debug = True

        if self.access_token:
            self._headers['Authorization'] = '{}'.format(self.access_token)
            
        url = ''.join([self.RootURL, url])
        
        my_request = urllib.request.Request(url, data, headers=self._headers, method=method)
        try:
            res = self.Opener.open(my_request, timeout=5)
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
            elif res.status == 401:
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                self.SetLogin( None, None)
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)

        return res

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