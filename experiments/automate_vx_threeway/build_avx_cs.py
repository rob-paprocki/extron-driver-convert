#!/usr/bin/env python3
"""
build_avx_cs.py - derive an improved Automate VX ControlScript module from Extron's own.

Why derive rather than write
----------------------------
Extron's onebynd_sm_Automate_VX_Series_v1_0_11_0.py is the code that works in the field. This
script applies a short list of NAMED edits to it, each fixing a defect that was reproduced by
running the module offline (experiments/exec_harness's extronlib stand-in against a loopback
server), or adding a call whose request and reply are documented. Everything not listed is
Extron's, byte for byte. Same pattern as experiments/skeleton_i20/build_i20.py.

The output starts with a provenance header. Then ten fixes, each marked [E#] where it occurs:
  E2  X25  SetScenario raised TypeError for the help sheet's own form (Value None, qualifier
           ID) and for any string. Accept either; discard anything that is not a whole number
           (fractions, infinity, True/False). A whole float such as 3.0 now sends "3".
  E3  X14  RoomConfiguration feedback read only the list shape; GetAllStatus documents an
           object. Accept both; TypeError no longer escapes
  E4  X17  Scenario feedback let KeyError and TypeError escape on an unexpected reply
  E5       a non-JSON, status-less or truncated reply raised into the caller, and a device
           error's reason was never printed
  E6  X24  a login reply without a token re-requested one with no limit (hundreds of requests
           in one burst, bounded only by the interpreter's recursion limit), and a null or
           empty token counted as logged in
  E7       a rejected token (401) was only logged, and every later call kept using it. Now the
           module logs in again and repeats that one request; if a fresh token is refused too,
           the login is kept (that request is not permitted) and nothing else is held up
  E8  X26  the first Set after start-up, or after the module declared Disconnected (which
           clears the token), was thrown away
  E9       a unit that was off, or refused the login, from start-up never set Connection Status
  E10 X16  camera feedback stored the reply's raw type (an int on the GetAllStatus shape), and
           a bad value raised; a fractional address is now logged, not truncated
  E11      five On/Off feedback parsers let TypeError escape on a malformed 'results'

Additions, marked [A#] (documented calls; replies parsed in every documented shape)
  A1  Record 'Pause'            POST api/PauseRecord
  A2  Update Layout             api/LayoutStatus (list or object)
  A3  ActiveTalker, DefaultShot api/GetActiveTalkers (firmware 6.3+; talkers is a string "[5,8]")
  A4  RecordingSpace            api/RecordingSpaceAvail (strings or numbers)
  A5  HealthStatus              api/HealthStatus (top-level status only)
  A6  LayoutName, RoomConfigurationName, ScenarioName, CameraModel, CameraCount
                                api/GetLayouts, GetRoomConfigs, GetScenarios, GetCameras

Left out on purpose: see BUILD.md.

Usage: python experiments/automate_vx_threeway/build_avx_cs.py [-o OUT]
Needs Extron's module (vendor material, untracked; vendor-files.manifest.tsv).
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
DONOR = os.path.join(_ROOT, "corpus", "extron-gs-modules", "09062026",
                     "onebynd_sm_Automate_VX_Series_v1_0_11_0.py")
OUT_NAME = "onebynd_sm_Automate_VX_Series_v1_1_0_0.py"
OUT = os.path.join(_HERE, "out", OUT_NAME)

HEADER = '''\
# Derived from Extron's onebynd_sm_Automate_VX_Series_v1_0_11_0.py by
# experiments/automate_vx_threeway/build_avx_cs.py. Fixes E2-E11 and additions A1-A6 are
# marked [E#] / [A#] where they occur; everything else is Extron's code, unchanged.
# Not tested on an Automate VX: see experiments/automate_vx_threeway/BUILD.md.
'''

EDITS = [
    ("E2", """    def SetScenario(self, value, qualifier):

        if 1 <= value:
""", """    def SetScenario(self, value, qualifier):

        # [E2] X25: the help sheet passes the ID as a qualifier with Value None, and a string
        # Value raised TypeError here. Accept either; discard anything that is not a whole number.
        if value is None and qualifier:
            value = qualifier.get('ID')
        try:
            number = int(value)
            if isinstance(value, bool) or (not isinstance(value, str) and number != value):
                number = 0
        except (TypeError, ValueError, OverflowError, ArithmeticError):
            number = 0
        value = number
        if 1 <= value:
"""),
    ("E3", """            try:
                value = str(res['roomConfigs'][0]['id'])
                self.WriteStatus('RoomConfiguration', value, qualifier)
            except (KeyError, IndexError, AttributeError):
""", """            try:
                # [E3] X14: the RoomConfigStatus page shows a list, GetAllStatus a single object
                if 'roomConfigs' in res:
                    value = str(res['roomConfigs'][0]['id'])
                else:
                    value = str(res['roomConfig']['id'])
                self.WriteStatus('RoomConfiguration', value, qualifier)
            except (KeyError, IndexError, AttributeError, TypeError):
"""),
    ("E4", """            except (ValueError, IndexError, AttributeError):
                self.Error(['Scenario: Invalid/unexpected response'])
""", """            except (KeyError, TypeError, ValueError, IndexError, AttributeError):  # [E4] X17
                self.Error(['Scenario: Invalid/unexpected response'])
"""),
    ("E5", """        try:
            res = json.loads(response.read().decode())
            if res['status'] == 'Error':
                self.Error(['Error:', res['err']])
                return ''
            return res
        except TypeError:
            self.Error(['Invalid Response'])
""", """        # [E5] a non-JSON, status-less or truncated reply raised into the caller, and the
        # device's error reason was never printed (Error prints only its first item)
        try:
            res = json.loads(response.read().decode())
            if res['status'] == 'Error':
                self.Error(['Error: {0}'.format(res.get('err'))])
                return ''
            return res
        except Exception:
            self.Error(['Invalid Response'])
"""),
    ("E6", """            try:
                self.Token = res['token'] # store token
                self.Authenticated = True # set to True if token in response
            except KeyError:
                self.Error(['Failed to obtain token'])
                self.TokenRequest( None, None)
""", """            try:
                # [E6] X24: a reply without a token asked again at once, with no limit, and a
                # null or empty token counted as logged in. The next Set or Update retries.
                token = res['token']
                if not token:
                    raise KeyError('token')
                self.Token = token # store token
                self.Authenticated = True # set to True if token in response
            except (KeyError, TypeError):
                self.Error(['Failed to obtain token'])
"""),
    ("E7 (Set, arguments)", """    def __SetHelper(self, command, value, qualifier, url='', data=None):

        self.Debug = True
""", """    def __SetHelper(self, command, value, qualifier, url='', data=None, retried=False):

        self.Debug = True
        retryArgs = (command, value, qualifier, url, data)  # [E7] to repeat once after a new login
"""),
    ("E7 (Set, 401)", """            except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
""", """            except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
                # [E7] a rejected token: log in again and repeat this request once. A fresh token
                # refused as well means this request is not permitted, so the login is kept.
                if err.code == 401 and command != 'TokenRequest' and not retried:
                    self.Authenticated = False
                    self.TokenRequest(None, None)
                    if self.Authenticated:
                        return self.__SetHelper(*retryArgs, retried=True)
"""),
    ("E7 (Update, arguments)", """    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.Authenticated:
""", """    def __UpdateHelper(self, command, value, qualifier, url='', data=None, retried=False):

        retryArgs = (command, value, qualifier, url, data)  # [E7] to repeat once after a new login
        if self.Authenticated:
"""),
    ("E7 (Update, 401)", """            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
""", """            except urllib.error.HTTPError as err: # includes HTTP status codes 101, 300-505
                self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
                res = ''
                # [E7] a rejected token: log in again and repeat this request once (see __SetHelper)
                if err.code == 401 and not retried:
                    self.Authenticated = False
                    self.TokenRequest(None, None)
                    if self.Authenticated:
                        return self.__UpdateHelper(*retryArgs, retried=True)
"""),
    ("E8", """        else:
            self.Discard('Invalid Command')
            self.TokenRequest(None, None)
""", """        else:
            # [E8] X26: the first Set after start-up, or after the module declared Disconnected,
            # was thrown away. Log in, then send it.
            self.TokenRequest(None, None)
            if self.Authenticated:
                return self.__SetHelper(command, value, qualifier, url, data)
            self.Discard('Invalid Command')
"""),
    ("E9", """        else:
            self.Error(['Token not obtained'])
            self.TokenRequest(None, None)
""", """        else:
            self.Error(['Token not obtained'])
            # [E9] a unit that was off, or refused the login, from start-up never set Connection Status
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.TokenRequest(None, None)
"""),
    ("E10", """                value = res['address']
                if 1 <= int(value) <= 255:
                    self.WriteStatus('SwitchCamera', value, qualifier)
            except (KeyError, IndexError, AttributeError):
""", """                # [E10] X16: the page shows a string, GetAllStatus a number; store '1'-'255' either way
                address = res['address']
                number = int(address)
                if isinstance(address, bool) or (not isinstance(address, str) and number != address):
                    raise ValueError(address)
                value = str(number)
                if 1 <= int(value) <= 255:
                    self.WriteStatus('SwitchCamera', value, qualifier)
            except (KeyError, IndexError, AttributeError, TypeError, ValueError, OverflowError):
"""),
]

for _label in ("Auto Switch", "ISO Recording", "Output", "Record", "Stream"):
    EDITS.append(("E11 (%s)" % _label,
                  "            except KeyError:\n                self.Error(['%s: Invalid/unexpected response'])\n" % _label,
                  "            except (KeyError, TypeError):  # [E11]\n"
                  "                self.Error(['%s: Invalid/unexpected response'])\n" % _label))

EDITS += [
    ("A1", """        ValueStateValues = {
            'Start' : 'api/StartRecord',
            'Stop'  : 'api/StopRecord'
        }
""", """        ValueStateValues = {
            'Start' : 'api/StartRecord',
            'Stop'  : 'api/StopRecord',
            'Pause' : 'api/PauseRecord'  # [A1] documented: no body, {"status":"OK",...}
        }
"""),
    ("A2-A6 (Commands)", """            'Zoom' : {'Parameters':['Camera'], 'Status': {}}
        }
""", """            'Zoom' : {'Parameters':['Camera'], 'Status': {}},
            # [A2-A6] status-only commands for documented calls Extron's driver did not make.
            # Qualifier values are strings ('1', 'A'), as in Extron's camera preset commands.
            'ActiveTalker' : {'Parameters':['Talker'], 'Status': {}},
            'CameraCount' : {'Status': {}},
            'CameraModel' : {'Parameters':['Camera'], 'Status': {}},
            'DefaultShot' : {'Status': {}},
            'HealthStatus' : {'Status': {}},
            'LayoutName' : {'Parameters':['Layout'], 'Status': {}},
            'RecordingSpace' : {'Parameters':['Type'], 'Status': {}},
            'RoomConfigurationName' : {'Parameters':['RoomConfiguration'], 'Status': {}},
            'ScenarioName' : {'Parameters':['Scenario'], 'Status': {}}
        }
"""),
]

NEW_METHODS = '''\
    # ---- [A2-A6] documented status calls -----------------------------------------------------
    # Each reply is parsed completely before anything is written, so a subscriber's callback
    # sees a consistent set and a callback's own error is not reported as a bad reply. Shapes
    # are the ones the API pages and the GetAllStatus example document; where they disagree,
    # both are accepted. None of it has been seen on a unit.

    def UpdateLayout(self, value, qualifier):  # [A2]

        res = self.__UpdateHelper('Layout', value, qualifier, 'api/LayoutStatus')
        if res:
            try:
                layout = res['layout']
                if isinstance(layout, list):  # the page shows a list, GetAllStatus an object
                    layout = layout[0]
                value = str(layout['id'])
            except (KeyError, IndexError, TypeError):
                self.Error(['Layout: Invalid/unexpected response'])
                return
            if len(value) == 1 and 'A' <= value <= 'Z':
                self.WriteStatus('Layout', value, qualifier)

    def __UpdateActiveTalkers(self, command, value, qualifier):  # [A3] firmware 6.3 and later

        res = self.__UpdateHelper(command, value, qualifier, 'api/GetActiveTalkers')
        if res:
            try:
                talkers = res['talkers']
                if isinstance(talkers, str):  # documented as a string: "[5,]", "[5,8]", "[ ]"
                    talkers = [t for t in talkers.strip().strip('[]').split(',') if t.strip()]
                positions = [str(int(t)) for t in talkers]
                flag = res.get('defaultShot', res.get('defaultshot'))  # the page spells it both ways
            except (KeyError, ValueError, TypeError):
                self.Error(['Active Talker: Invalid/unexpected response'])
                return
            if flag in (0, 1):
                self.WriteStatus('DefaultShot', 'On' if flag else 'Off')
            for slot in (1, 0):
                self.WriteStatus('ActiveTalker', positions[slot] if slot < len(positions) else 'None',
                                 {'Talker': str(slot + 1)})

    def UpdateActiveTalker(self, value, qualifier):  # [A3]

        self.__UpdateActiveTalkers('ActiveTalker', value, qualifier)

    def UpdateDefaultShot(self, value, qualifier):  # [A3]

        self.__UpdateActiveTalkers('DefaultShot', value, qualifier)

    def UpdateRecordingSpace(self, value, qualifier):  # [A4]

        res = self.__UpdateHelper('RecordingSpace', value, qualifier, 'api/RecordingSpaceAvail')
        if res:
            try:  # the page shows quoted strings, the GetAllStatus example numbers
                available = int(float(res['available_gigabytes']))
                total = int(float(res['total_gigabytes']))
            except (KeyError, ValueError, TypeError, OverflowError):
                self.Error(['Recording Space: Invalid/unexpected response'])
                return
            self.WriteStatus('RecordingSpace', total, {'Type': 'Total'})
            self.WriteStatus('RecordingSpace', available, {'Type': 'Available'})

    def UpdateHealthStatus(self, value, qualifier):  # [A5] top-level status only ('Healthy')

        res = self.__UpdateHelper('HealthStatus', value, qualifier, 'api/HealthStatus')
        if res:
            try:
                value = str(res['status'])
            except (KeyError, TypeError):
                self.Error(['Health Status: Invalid/unexpected response'])
                return
            self.WriteStatus('HealthStatus', value)

    def __ReadNames(self, res, listKey, label, nameKeys=('name',)):  # [A6]

        try:
            names = {}
            for item in res[listKey]:
                name = ''
                for key in nameKeys:
                    if key in item:
                        name = str(item[key])
                        break
                names[str(item['id'])] = name
            return names
        except (KeyError, TypeError):
            self.Error(['{0}: Invalid/unexpected response'.format(label)])
            return None

    def __WriteNames(self, command, qualifierKey, names):  # [A6] also blanks entries no longer listed

        for key in names:
            self.WriteStatus(command, names[key], {qualifierKey: key})
        for key in [k for k in self.Commands[command]['Status'] if k != 'Live' and k not in names]:
            self.WriteStatus(command, '', {qualifierKey: key})

    def UpdateLayoutName(self, value, qualifier):  # [A6]

        res = self.__UpdateHelper('LayoutName', value, qualifier, 'api/GetLayouts')
        if res:
            names = self.__ReadNames(res, 'layouts', 'Layout Name')
            if names is not None:
                self.__WriteNames('LayoutName', 'Layout', names)

    def UpdateRoomConfigurationName(self, value, qualifier):  # [A6] ids quoted on the page, numbers in GetAllStatus

        res = self.__UpdateHelper('RoomConfigurationName', value, qualifier, 'api/GetRoomConfigs')
        if res:
            names = self.__ReadNames(res, 'roomConfigs', 'Room Configuration Name')
            if names is not None:
                self.__WriteNames('RoomConfigurationName', 'RoomConfiguration', names)

    def UpdateScenarioName(self, value, qualifier):  # [A6]

        res = self.__UpdateHelper('ScenarioName', value, qualifier, 'api/GetScenarios')
        if res:
            names = self.__ReadNames(res, 'scenarios', 'Scenario Name')
            if names is not None:
                self.__WriteNames('ScenarioName', 'Scenario', names)

    def __UpdateCameras(self, command, value, qualifier):  # [A6] the page's "name" is a model name

        res = self.__UpdateHelper(command, value, qualifier, 'api/GetCameras')
        if res:
            models = self.__ReadNames(res, 'cameras', 'Camera Model', nameKeys=('name', 'model'))
            if models is not None:
                self.__WriteNames('CameraModel', 'Camera', models)
                self.WriteStatus('CameraCount', len(models))

    def UpdateCameraModel(self, value, qualifier):  # [A6]

        self.__UpdateCameras('CameraModel', value, qualifier)

    def UpdateCameraCount(self, value, qualifier):  # [A6]

        self.__UpdateCameras('CameraCount', value, qualifier)

'''
METHODS_ANCHOR = "    def __CheckResponseForErrors(self, sourceCmdName, response):\n"


class BuildError(Exception):
    pass


def build(donor_text):
    """Extron's module text (any line endings) -> the derived module text (LF line endings)."""
    src = donor_text.replace("\r\n", "\n")
    for label, old, new in EDITS:
        n = src.count(old)
        if n != 1:
            raise BuildError("%s: anchor found %d times, expected 1" % (label, n))
        src = src.replace(old, new)
    if src.count(METHODS_ANCHOR) != 1:
        raise BuildError("methods anchor not found exactly once")
    src = src.replace(METHODS_ANCHOR, NEW_METHODS + METHODS_ANCHOR)
    first, rest = src.split("\n", 1)                    # keep Extron's copyright line first
    return first + "\n" + HEADER + rest


def main(argv=None):
    ap = argparse.ArgumentParser(description="Derive the improved Automate VX ControlScript module.")
    ap.add_argument("-o", "--out", default=OUT)
    args = ap.parse_args(argv)
    if not os.path.isfile(DONOR):
        print("Extron's module is not on disk (vendor material): %s" % os.path.relpath(DONOR, _ROOT))
        return 1
    with open(DONOR, encoding="utf-8", newline="") as f:
        text = build(f.read())
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\r\n") as f:   # Extron's line endings
        f.write(text)
    print("wrote %s (%d anchored edits, plus the A2-A6 methods)" % (
        os.path.relpath(args.out, _ROOT).replace(os.sep, "/"), len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
