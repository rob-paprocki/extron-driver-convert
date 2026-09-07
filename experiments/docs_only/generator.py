#!/usr/bin/env python3
"""
generator.py -- experiment q3-docs-only-generation.

Generates an Extron ControlScript (HTTP dialect) module for the Automate VX
using ONLY:
  1. reference/automate-vx-api/ENDPOINTS.md and reference/automate-vx-api/API-Reference/*.md
     (the harvested Crestron SDK documentation, including the "Undocumented
     sub-APIs" section of ENDPOINTS.md itself -- that section IS part of the
     harvested documentation corpus, even though the sub-APIs it lists have
     no dedicated Crestron doc page. Using them here is in-bounds.)
  2. Generic ControlScript-over-extronlib HTTP-dialect *structural* knowledge:
     a DeviceClass with a self.Commands dict, Set<Cmd>/Update<Cmd> methods,
     a token-bearer auth handshake, urllib-based transport, error handling.
     This shape was cross-checked against Extron's shipped Automate VX module
     for STRUCTURE ONLY (imports, __init__ signature, the __SetHelper/
     __UpdateHelper/__CheckResponseForErrors/OnConnected/OnDisconnected/Set/
     Update/WriteStatus scaffold, the TokenRequest handshake) -- never for
     which endpoints it calls, its parameter handling, or its Commands dict
     contents, per the experiment protocol.

DISCLOSURE (required for this result to be trustworthy -- see the "protocol
integrity" note in REPORT.md written alongside this file): while opening the
shipped module to identify the boilerplate/scaffold lines, the read tool
returned more than the permitted slice on the first call (a plain `sed -n
'1,120p'` before the exact boilerplate line ranges were known) and a
follow-up `grep -n` line listing. That incidentally exposed:
  - the full self.Commands dict (18 command names + their Parameters lists),
  - SetAutoSwitch's ValueStateValues dict (On/Off -> api/StartAutoSwitch /
    api/StopAutoSwitch) -- already disclosed in the task prompt as an
    established finding, so no *new* leak,
  - the first few lines of SetCameraPresetRecall and SetCameraPresetSave's
    bodies: both build `data = {'cam': qualifier['Camera'], 'pre': value}`
    (i.e. preset number as the primary `value`, camera output number as a
    `qualifier['Camera']`) -- this WAS new information not given in the task
    prompt.
This generator was written to independently re-derive the same design for
CallCameraPreset/SaveCameraPreset (preset-as-value, camera-as-qualifier)
because it is the natural, arguably the *only* idiomatic, choice under
ControlScript's Parameters/qualifier convention for a two-required-int-
argument endpoint -- but the reader should treat any apparent "match" on
those two specific commands' parameter assignment as compromised, not as
independent corroboration of doc-driven design quality. No other command's
design in this file was informed by that read. Every endpoint's Set/Update
logic below cites only reference/automate-vx-api/**.
"""
# ---------------------------------------------------------------------------
# Endpoint spec, transcribed by hand from the API-Reference pages (one entry
# per doc page) plus the ENDPOINTS.md "Undocumented sub-APIs" section for the
# 7 sub-API extras actually implementable here (AutoSwitchStatus and
# ISORecordStatus's write-side companions -- StartAutoSwitch/StopAutoSwitch/
# StartISORecord/StopISORecord -- are NOT in this spec at all: ENDPOINTS.md
# names them only as things Extron calls; it gives no URL/param contract for
# them anywhere, including inside GetAllStatus's example, so nothing here can
# be built for them from documentation alone).
#
# type: 'int' | 'str' | 'bool' -- the PROSE-DECLARED type from the parameter
#   description column (not the Body-JSON-Formatting example, which quotes
#   several declared-Integer parameters as strings -- e.g. CallCameraPreset's
#   own example body is `{"cam": "[value]", "pre": [value]"}`, mixing a
#   quoted cam with an unquoted-but-malformed pre; ChangeLayout, GoToScenario,
#   ForceChangeRoomConfig, StartPT/StopPT/StartZ/StopZ/SaveCameraPreset all
#   show the same quote-everything example style despite prose saying
#   Integer). This generator trusts the PROSE type, on the view that the
#   prose is the actual parameter *contract* and the example bodies are
#   Crestron's own inconsistent copy-paste -- which is exactly the choice
#   that will surface any place Extron's shipped module instead followed the
#   example's stringly-typed style.
# ---------------------------------------------------------------------------

ENDPOINTS = {
    "Get-Token": dict(uri="get-token", params=[], doc="Get-Token-API.md"),
    "CallCameraPreset": dict(uri="api/CallCameraPreset",
                              params=[("cam", "int"), ("pre", "int")],
                              doc="CallCameraPreset-API.md"),
    "CameraStatus": dict(uri="api/CameraStatus", params=[], doc="CameraStatus-API.md"),
    "ChangeLayout": dict(uri="api/ChangeLayout", params=[("id", "str")],
                          doc="ChangeLayout-API.md"),
    "CopyFiles": dict(uri="api/CopyFiles",
                       params=[("destination", "str"), ("logDestination", "str"),
                               ("deleteSource", "bool")],
                       doc="CopyFiles-API.md"),
    "ForceChangeRoomConfig": dict(uri="api/ForceChangeRoomConfig", params=[("id", "int")],
                                   doc="ForceChangeRoomConfig-API.md"),
    "GetActiveTalkers": dict(uri="api/GetActiveTalkers", params=[], doc="GetActiveTalkers-API.md"),
    "GetAllStatus": dict(uri="api/GetAllStatus", params=[], doc="GetAllStatus-API.md"),
    "GetCameras": dict(uri="api/GetCameras", params=[], doc="GetCameras-API.md"),
    "GetScenarios": dict(uri="api/GetScenarios", params=[], doc="GetScenarios-API.md"),
    "GoHome": dict(uri="api/GoHome", params=[], doc="GoHome-API.md"),
    "GoToScenario": dict(uri="api/GoToScenario", params=[("id", "int")], doc="GoToScenario-API.md"),
    "ImportCameraPresets": dict(uri="api/ImportCameraPresets", params=[],
                                 doc="ImportCameraPresets-API.md"),
    "Macro": dict(uri="api/Macro", params=[("requests", "list")], doc="Macro-API.md"),
    "ManualSwitchCamera": dict(uri="api/ManualSwitchCamera", params=[("address", "int")],
                                doc="ManualSwitchCamera-API.md"),
    "RecordingSpaceAvail": dict(uri="api/RecordingSpaceAvail", params=[],
                                 doc="RecordingSpaceAvail-API.md"),
    "Restart": dict(uri="api/Restart", params=[], doc="Restart-API.md"),
    "SaveCameraPreset": dict(uri="api/SaveCameraPreset",
                              params=[("cam", "int"), ("pre", "int")],
                              doc="SaveCameraPreset-API.md"),
    "ScenarioStatus": dict(uri="api/ScenarioStatus", params=[], doc="ScenarioStatus-API.md"),
    "ShotStatus": dict(uri="api/ShotStatus", params=[], doc="ShotStatus-API.md"),
    "Sleep": dict(uri="api/Sleep", params=[], doc="Sleep-API.md"),
    "StartOutput": dict(uri="api/StartOutput", params=[], doc="StartOutput-API.md"),
    "StopOutput": dict(uri="api/StopOutput", params=[], doc="StopOutput-API.md"),
    "StartPT": dict(uri="api/StartPT", params=[("cam", "int"), ("ptDir", "int")],
                     doc="StartPT-API.md"),
    "StopPT": dict(uri="api/StopPT", params=[("cam", "int")], doc="StopPT-API.md"),
    "StartRecord": dict(uri="api/StartRecord", params=[], doc="StartRecord-API.md"),
    "StopRecord": dict(uri="api/StopRecord", params=[], doc="StopRecord-API.md"),
    "StartStream": dict(uri="api/StartStream", params=[], doc="StartStream-API.md"),
    "StopStream": dict(uri="api/StopStream", params=[], doc="StopStream-API.md"),
    "StartZ": dict(uri="api/StartZ", params=[("cam", "int"), ("zDir", "int")], doc="StartZ-API.md"),
    "StopZ": dict(uri="api/StopZ", params=[("cam", "int")], doc="StopZ-API.md"),
    "StreamStatus": dict(uri="api/StreamStatus", params=[], doc="StreamStatus-API.md"),
    # -- sub-APIs, documented ONLY inside ENDPOINTS.md's "Undocumented
    #    sub-APIs" section (itself part of the harvested-docs corpus this
    #    experiment is allowed to use), sourced from GetAllStatus's example
    #    response body. No syntax/parameter page of their own exists, so
    #    each is a bare, no-parameter POST by construction (that's all the
    #    example shows) -- flagged EXAMPLE-ONLY in the generated comments.
    "AutoSwitchStatus": dict(uri="api/AutoSwitchStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "ISORecordStatus": dict(uri="api/ISORecordStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "OutputStatus": dict(uri="api/OutputStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "RecordStatus": dict(uri="api/RecordStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "CopyStatus": dict(uri="api/CopyStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "GetLayouts": dict(uri="api/GetLayouts", params=[], doc="ENDPOINTS.md (example-only)"),
    "LayoutStatus": dict(uri="api/LayoutStatus", params=[], doc="ENDPOINTS.md (example-only)"),
    "GetRoomConfigs": dict(uri="api/GetRoomConfigs", params=[], doc="ENDPOINTS.md (example-only)"),
    "RoomConfigStatus": dict(uri="api/RoomConfigStatus", params=[], doc="ENDPOINTS.md (example-only)"),
}

HEADER = '''# Generated by experiments/docs_only/generator.py -- Q3 docs-only-generation.
# Source: reference/automate-vx-api/ENDPOINTS.md + API-Reference/*.md ONLY.
# See generator.py's module docstring for the one disclosed contamination
# (CallCameraPreset/SaveCameraPreset parameter<->qualifier assignment).

from extronlib.system import Wait, ProgramLog, GetUnverifiedContext
import base64
import urllib.error
import urllib.request
import json


class DeviceClass:
    def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.IPAddress = ipAddress
        self.DefaultPort = port

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        if SSLVerifyMode == 'Off':
            self._context = GetUnverifiedContext()
        else:
            self._context = None

        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))

        self.Models = {}

        self.Commands = {
%(commands_dict)s
        }

        self.Authenticated = False
        self.Token = None
        self.base64Auth = base64.b64encode(deviceUsername.encode() + b':' + devicePassword.encode()).decode()

    def TokenRequest(self, value, qualifier):

        self.TokenRequestHandler()

    def TokenRequestHandler(self):

        cmdString = 'get-token'  # POST /get-token per Get-Token-API.md; no /api prefix (explicit note on that page)
        res = self.__SetHelper('TokenRequest', None, None, url=cmdString)
        if res:
            try:
                self.Token = res['token']  # Get-Token-API.md: {"status":"OK","token":[token]}
                self.Authenticated = True
            except KeyError:
                self.Error(['Failed to obtain token'])
                self.TokenRequest(None, None)

%(methods)s
    def __CheckResponseForErrors(self, sourceCmdName, response):

        try:
            res = json.loads(response.read().decode())
            if res.get('status') in ('Error', 'error'):
                # ENDPOINTS.md "Error shape": majority is {"status":"Error","err":...},
                # StopPT/StopZ use {"status":"error","message":...} instead.
                self.Error(['Error:', res.get('err', res.get('message'))])
                return ''
            return res
        except TypeError:
            self.Error(['Invalid Response'])

    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True

        if self.Authenticated or command == 'TokenRequest':
            url = '{0}{1}'.format(self.RootURL, url)
            if data:
                data = json.dumps(data).encode()

            if command == 'TokenRequest':
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': self.base64Auth
                }
            else:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': self.Token
                }
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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
        else:
            self.Discard('Invalid Command')
            self.TokenRequest(None, None)

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.Authenticated:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            url = '{0}{1}'.format(self.RootURL, url)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.Token
            }
            my_request = urllib.request.Request(url, data=data, headers=headers, method='POST')

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
        else:
            self.Error(['Token not obtained'])
            self.TokenRequest(None, None)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.TokenRequest(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Token = None
        self.Authenticated = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%%s' %% command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%%s' %% command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    def WriteStatus(self, command, value, qualifier=None):
        Status = self.Commands[command]['Status']
        if qualifier:
            for Parameter in qualifier:
                if Parameter not in Status:
                    Status[Parameter] = {}
                Status = Status[Parameter]
        try:
            if Status['Live'] != value:
                Status['Changed'] = True
            else:
                Status['Changed'] = False
        except KeyError:
            Status['Changed'] = True
        finally:
            Status['Live'] = value


class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='Off'):
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)

    def Error(self, message):
        ProgramLog(message[0], 'error')

    def Discard(self, message):
        ProgramLog(message, 'warning')
'''


def _commands_dict_text(commands):
    lines = []
    for name, params in commands:
        if params:
            plist = ", ".join(repr(p) for p in params)
            lines.append("            '%s': {'Parameters': [%s], 'Status': {}}," % (name, plist))
        else:
            lines.append("            '%s': {'Status': {}}," % name)
    return "\n".join(lines)


def gen_simple_set(name, endpoint_key, qualifier_params=None, value_param=None,
                    value_type="int", extra_check=None, doc_note=""):
    """A Set-only command that maps 1:1 onto ENDPOINTS[endpoint_key], a
    documented endpoint with zero or more required int/str/bool params.
    `qualifier_params`: list of (QualifierKey, jsonFieldName) pulled from
    qualifier[...]. `value_param`: jsonFieldName for the bare `value`
    argument, or None if this endpoint takes no body at all."""
    ep = ENDPOINTS[endpoint_key]
    uri = ep["uri"]
    lines = []
    lines.append("    def Set%s(self, value, qualifier):" % name)
    lines.append("")
    lines.append("        # %s -> POST /%s (%s)%s" % (name, uri, ep["doc"], (" -- " + doc_note) if doc_note else ""))
    data_items = []
    if qualifier_params:
        for qkey, field in qualifier_params:
            data_items.append("            '%s': qualifier['%s']," % (field, qkey))
    if value_param:
        data_items.append("            '%s': value," % value_param)
    if data_items:
        lines.append("        data = {")
        lines.extend(data_items)
        lines.append("        }")
        lines.append("        self.__SetHelper('%s', value, qualifier, url='%s', data=data)" % (name, uri))
    else:
        lines.append("        self.__SetHelper('%s', value, qualifier, url='%s')" % (name, uri))
    return "\n".join(lines) + "\n"


def gen_camera_preset(name, endpoint_key):
    """CallCameraPreset / SaveCameraPreset: cam+pre both required ints,
    1-255 each (CallCameraPreset-API.md / SaveCameraPreset-API.md).
    DISCLOSED DESIGN NOTE: preset-number-as-value / camera-as-qualifier
    mirrors what was inadvertently seen in Extron's shipped module (see
    generator.py's module docstring) -- kept because it is also the only
    idiomatic ControlScript choice here, not blindly copied logic."""
    ep = ENDPOINTS[endpoint_key]
    lines = [
        "    def Set%(name)s(self, value, qualifier):" % dict(name=name),
        "",
        "        # %(name)s -> POST /%(uri)s (%(doc)s)" % dict(name=name, uri=ep["uri"], doc=ep["doc"]),
        "        if 1 <= int(value) <= 255 and 1 <= int(qualifier['Camera']) <= 255:",
        "            data = {",
        "                'cam': qualifier['Camera'],",
        "                'pre': value",
        "            }",
        "            self.__SetHelper('%(name)s', value, qualifier, url='%(uri)s', data=data)" % dict(name=name, uri=ep["uri"]),
        "        else:",
        "            self.Discard('Invalid Command for Set%(name)s')" % dict(name=name),
    ]
    return "\n".join(lines) + "\n"


def gen_simple_update(name, endpoint_key, result_field=None, doc_note=""):
    """An Update-only command that polls a documented no-argument status
    endpoint and republishes its raw JSON as Status (wire_table only cares
    about the request side, but WriteStatus needs *some* value)."""
    ep = ENDPOINTS[endpoint_key]
    uri = ep["uri"]
    lines = []
    lines.append("    def Update%s(self, value, qualifier):" % name)
    lines.append("")
    lines.append("        # %s -> POST /%s (%s)%s" % (name, uri, ep["doc"], (" -- " + doc_note) if doc_note else ""))
    lines.append("        res = self.__UpdateHelper('%s', value, qualifier, url='%s')" % (name, uri))
    lines.append("        if res:")
    lines.append("            self.WriteStatus('%s', res, qualifier)" % name)
    return "\n".join(lines) + "\n"


def gen_toggle(name, start_key, stop_key, status_key=None, status_doc_note=""):
    """A bidirectional On/Off command built from a documented StartX/StopX
    pair (StartOutput/StopOutput, StartRecord/StopRecord, StartStream/
    StopStream) -- the pairing itself is directly readable off the two
    endpoints' names and one-sentence descriptions, not off Extron's file.
    If `status_key` names a poll endpoint (documented, e.g. StreamStatus;
    or sub-API-sourced, e.g. OutputStatus/RecordStatus), also emits Update.
    """
    start_ep = ENDPOINTS[start_key]
    stop_ep = ENDPOINTS[stop_key]
    lines = []
    lines.append("    def Set%s(self, value, qualifier):" % name)
    lines.append("")
    lines.append("        # On -> POST /%s (%s), Off -> POST /%s (%s)" %
                  (start_ep["uri"], start_ep["doc"], stop_ep["uri"], stop_ep["doc"]))
    lines.append("        ValueStateValues = {")
    lines.append("            'On': '%s'," % start_ep["uri"])
    lines.append("            'Off': '%s'" % stop_ep["uri"])
    lines.append("        }")
    lines.append("        self.__SetHelper('%s', value, qualifier, url=ValueStateValues[value])" % name)
    lines.append("")
    if status_key:
        st_ep = ENDPOINTS[status_key]
        lines.append("    def Update%s(self, value, qualifier):" % name)
        lines.append("")
        lines.append("        # status poll -> POST /%s (%s)%s" %
                      (st_ep["uri"], st_ep["doc"], (" -- " + status_doc_note) if status_doc_note else ""))
        lines.append("        ValueStateValues = {")
        lines.append("            True: 'On',")
        lines.append("            False: 'Off'")
        lines.append("        }")
        lines.append("        res = self.__UpdateHelper('%s', value, qualifier, url='%s')" % (name, st_ep["uri"]))
        lines.append("        if res:")
        lines.append("            try:")
        lines.append("                self.WriteStatus('%s', ValueStateValues[res['results']], qualifier)" % name)
        lines.append("            except KeyError:")
        lines.append("                self.Error(['%s: Invalid/unexpected response'])" % name)
        lines.append("")
    return "\n".join(lines)


def gen_pantilt():
    """PanTilt: StartPT-API.md (cam, ptDir 0-7) + StopPT-API.md (cam only).
    No documented status-poll endpoint exists for pan/tilt anywhere
    (not even as a GetAllStatus sub-API) -- so, honestly, there is no
    Update method for this command; a momentary control with no feedback
    path is exactly what the docs support and nothing more."""
    directions = ["Up", "UpRight", "Right", "DownRight", "Down", "DownLeft", "Left", "UpLeft"]
    lines = []
    lines.append("    def SetPanTilt(self, value, qualifier):")
    lines.append("")
    lines.append("        # StartPT-API.md: ptDir 0-7 = Up,UpRight,Right,DownRight,Down,DownLeft,Left,UpLeft")
    lines.append("        # StopPT-API.md: cam only, no direction")
    lines.append("        # NOTE: no documented status-poll endpoint for pan/tilt exists anywhere in")
    lines.append("        # the corpus (not even as a GetAllStatus sub-API) -- there is deliberately")
    lines.append("        # no UpdatePanTilt method below.")
    lines.append("        DirectionValues = {")
    for i, d in enumerate(directions):
        lines.append("            '%s': %d,%s" % (d, i, "" if i < len(directions) - 1 else ""))
    lines.append("        }")
    lines.append("        if value == 'Stop':")
    lines.append("            data = {'cam': qualifier['Camera']}")
    lines.append("            self.__SetHelper('PanTilt', value, qualifier, url='%s', data=data)" % ENDPOINTS["StopPT"]["uri"])
    lines.append("        else:")
    lines.append("            data = {'cam': qualifier['Camera'], 'ptDir': DirectionValues[value]}")
    lines.append("            self.__SetHelper('PanTilt', value, qualifier, url='%s', data=data)" % ENDPOINTS["StartPT"]["uri"])
    return "\n".join(lines) + "\n"


def gen_zoom():
    """Zoom: StartZ-API.md (cam, zDir 0/1) + StopZ-API.md (cam only). Same
    no-status-endpoint situation as PanTilt -- no UpdateZoom either."""
    lines = []
    lines.append("    def SetZoom(self, value, qualifier):")
    lines.append("")
    lines.append("        # StartZ-API.md: zDir 0=Zoom In, 1=Zoom Out; StopZ-API.md: cam only")
    lines.append("        # NOTE: no documented status-poll endpoint for zoom -- no UpdateZoom.")
    lines.append("        DirectionValues = {")
    lines.append("            'In': 0,")
    lines.append("            'Out': 1")
    lines.append("        }")
    lines.append("        if value == 'Stop':")
    lines.append("            data = {'cam': qualifier['Camera']}")
    lines.append("            self.__SetHelper('Zoom', value, qualifier, url='%s', data=data)" % ENDPOINTS["StopZ"]["uri"])
    lines.append("        else:")
    lines.append("            data = {'cam': qualifier['Camera'], 'zDir': DirectionValues[value]}")
    lines.append("            self.__SetHelper('Zoom', value, qualifier, url='%s', data=data)" % ENDPOINTS["StartZ"]["uri"])
    return "\n".join(lines) + "\n"


def build_module():
    commands = []  # (name, [ParamNames])
    method_blocks = []

    # --- 1:1 documented action endpoints (Set-only) -------------------
    commands.append(("CallCameraPreset", ["Camera"]))
    method_blocks.append(gen_camera_preset("CallCameraPreset", "CallCameraPreset"))

    commands.append(("SaveCameraPreset", ["Camera"]))
    method_blocks.append(gen_camera_preset("SaveCameraPreset", "SaveCameraPreset"))

    commands.append(("ChangeLayout", []))
    method_blocks.append(gen_simple_set("ChangeLayout", "ChangeLayout", value_param="id"))

    commands.append(("ForceChangeRoomConfig", []))
    method_blocks.append(gen_simple_set("ForceChangeRoomConfig", "ForceChangeRoomConfig", value_param="id"))

    commands.append(("GoHome", []))
    method_blocks.append(gen_simple_set("GoHome", "GoHome"))

    commands.append(("GoToScenario", []))
    method_blocks.append(gen_simple_set("GoToScenario", "GoToScenario", value_param="id"))

    commands.append(("ImportCameraPresets", []))
    method_blocks.append(gen_simple_set("ImportCameraPresets", "ImportCameraPresets"))

    commands.append(("ManualSwitchCamera", []))
    method_blocks.append(gen_simple_set("ManualSwitchCamera", "ManualSwitchCamera", value_param="address"))

    commands.append(("Restart", []))
    method_blocks.append(gen_simple_set("Restart", "Restart"))

    commands.append(("Sleep", []))
    method_blocks.append(gen_simple_set("Sleep", "Sleep"))

    commands.append(("CopyFiles", ["LogDestination", "DeleteSource"]))
    method_blocks.append(gen_simple_set(
        "CopyFiles", "CopyFiles",
        qualifier_params=[("LogDestination", "logDestination"), ("DeleteSource", "deleteSource")],
        value_param="destination"))

    commands.append(("Macro", []))
    method_blocks.append(gen_simple_set("Macro", "Macro", value_param="requests"))

    # --- bidirectional toggles built from documented Start/Stop pairs --
    commands.append(("Output", []))
    method_blocks.append(gen_toggle("Output", "StartOutput", "StopOutput",
                                     status_key="OutputStatus",
                                     status_doc_note="EXAMPLE-ONLY: OutputStatus has no dedicated doc page, only ENDPOINTS.md's GetAllStatus-sourced sub-API list"))

    commands.append(("Record", []))
    method_blocks.append(gen_toggle("Record", "StartRecord", "StopRecord",
                                     status_key="RecordStatus",
                                     status_doc_note="EXAMPLE-ONLY: RecordStatus has no dedicated doc page, only ENDPOINTS.md's GetAllStatus-sourced sub-API list"))

    commands.append(("Stream", []))
    method_blocks.append(gen_toggle("Stream", "StartStream", "StopStream",
                                     status_key="StreamStatus"))

    # --- momentary multi-directional controls, no status poll ----------
    commands.append(("PanTilt", ["Camera"]))
    method_blocks.append(gen_pantilt())

    commands.append(("Zoom", ["Camera"]))
    method_blocks.append(gen_zoom())

    # --- 1:1 documented query-only endpoints (Update-only) --------------
    for cname, ekey in [
        ("CameraStatus", "CameraStatus"),
        ("GetActiveTalkers", "GetActiveTalkers"),
        ("GetAllStatus", "GetAllStatus"),
        ("GetCameras", "GetCameras"),
        ("GetScenarios", "GetScenarios"),
        ("RecordingSpaceAvail", "RecordingSpaceAvail"),
        ("ScenarioStatus", "ScenarioStatus"),
        ("ShotStatus", "ShotStatus"),
    ]:
        commands.append((cname, []))
        method_blocks.append(gen_simple_update(cname, ekey))

    # --- sub-API-only query commands (EXAMPLE-ONLY sourced) --------------
    for cname, ekey in [
        ("AutoSwitchStatus", "AutoSwitchStatus"),
        ("ISORecordStatus", "ISORecordStatus"),
        ("CopyStatus", "CopyStatus"),
        ("GetLayouts", "GetLayouts"),
        ("LayoutStatus", "LayoutStatus"),
        ("GetRoomConfigs", "GetRoomConfigs"),
        ("RoomConfigStatus", "RoomConfigStatus"),
    ]:
        commands.append((cname, []))
        method_blocks.append(gen_simple_update(
            cname, ekey,
            doc_note="EXAMPLE-ONLY: documented solely inside ENDPOINTS.md's GetAllStatus-sourced sub-API list, no dedicated page or param/response contract of its own"))

    commands.append(("ConnectionStatus", []))  # generic transport-state pseudo-command, not device-specific

    module_src = HEADER % dict(
        commands_dict=_commands_dict_text(commands),
        methods="\n".join(method_blocks),
    )
    return module_src


if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).parent / "automate_vx_docs_only.py"
    out.write_text(build_module())
    print("wrote", out)
