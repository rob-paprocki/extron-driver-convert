"""
extronlib_stub.py - a stand-in for Extron's extronlib, enough to import and
drive a ControlScript device module offline and record what it would send.

Written for this harness from the public class and method names in Extron's
ControlScript VS Code extension stubs (extronlib 1.10.0xi); no vendor code is
copied, and the extension is not needed to run it. install() puts a finder on
sys.meta_path so that every `extronlib.*` import resolves:

- EthernetClientInterface, SerialInterface and the server interfaces record
  every Send / SendAndWait in `self._harness_sent` instead of opening a port.
  SendAndWait returns None (no device answered), which every module under
  comparison receives alike.
- Wait and Timer record and never fire, as a decorator or called directly: no
  background threads, and identical treatment for both sides of a comparison.
- ProgramLog records.
- `extronlib.standard.exml.etree.*` is the standard library's xml.etree: the
  one shipped module seen importing it (Panopto Remote Recorder) uses it as an
  ElementTree.
- Any other name in any extronlib module is an inert placeholder, so a device
  module that imports a UI class it never uses still loads. A placeholder
  called with a single function returns it, so `@event(...)` decorates.

Standard library only.
"""
import importlib.abc
import importlib.machinery
import sys
import types

PROGRAM_LOG = []          # (message, severity) from ProgramLog()
WAITS = []                # every Wait / Timer created, never fired


def _to_bytes(data):
    """What a Send puts on the wire, as bytes, whatever type it was given."""
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    if isinstance(data, str):
        try:
            return data.encode("latin-1")
        except UnicodeEncodeError:
            return data.encode("utf-8")
    return repr(data).encode("utf-8")


class _Placeholder:
    """Any extronlib name the harness does not model."""

    def __init__(self, *args, **kwargs):
        self._harness_args = args

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0], types.FunctionType):
            return args[0]          # used as a decorator
        return _Placeholder()

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return _Placeholder()


class _Interface:
    """Common recording behaviour of the transport interfaces."""

    def _harness_init(self):
        self._harness_sent = []
        self._harness_keepalive = None

    def Send(self, data):
        self._harness_sent.append(("Send", _to_bytes(data)))

    def SendAndWait(self, data, timeout=None, **delimiter):
        self._harness_sent.append(("SendAndWait", _to_bytes(data)))
        return None

    def Connect(self, timeout=None):
        return "Connected"

    def Disconnect(self):
        return None

    def StartKeepAlive(self, interval, data):
        self._harness_keepalive = (interval, _to_bytes(data))

    def StopKeepAlive(self):
        self._harness_keepalive = None

    def Initialize(self, *args, **kwargs):
        return None


class EthernetClientInterface(_Interface):
    def __init__(self, Hostname, IPPort, Protocol="TCP", ServicePort=0,
                 Credentials=None, bufferSize=4096):
        self._harness_init()
        self.Hostname = Hostname
        self.IPPort = IPPort
        self.Protocol = Protocol
        self.ServicePort = ServicePort
        self.Credentials = Credentials


class SerialInterface(_Interface):
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity="None", Stop=1,
                 FlowControl="Off", CharDelay=0, Mode="RS232"):
        self._harness_init()
        self.Host = Host
        self.Port = Port
        self.Baud = Baud
        self.Data = Data
        self.Parity = Parity
        self.Stop = Stop
        self.FlowControl = FlowControl
        self.CharDelay = CharDelay
        self.Mode = Mode


class EthernetServerInterfaceEx(_Interface):
    def __init__(self, IPPort, Protocol="TCP", Interface="Any", MaxClients=None):
        self._harness_init()
        self.IPPort = IPPort
        self.Protocol = Protocol


EthernetServerInterface = EthernetServerInterfaceEx


class Wait:
    """extronlib.system.Wait(Time, Function) or @Wait(Time). Never fires."""

    def __init__(self, Time, Function=None):
        self.Time = Time
        self.Function = Function
        WAITS.append(self)

    def __call__(self, function):
        self.Function = function
        return self

    def Add(self, Time):
        self.Time += Time

    def Cancel(self):
        return None

    def Change(self, Time):
        self.Time = Time

    def Restart(self):
        return None


class Timer(Wait):
    """extronlib.system.Timer(Interval, Function) or @Timer(Interval). Never fires."""

    def __init__(self, Interval, Function=None):
        Wait.__init__(self, Interval, Function)
        self.Interval = Interval
        self.Count = 0
        self.State = "Running"

    def Stop(self):
        self.State = "Stopped"

    def Pause(self):
        self.State = "Paused"

    def Resume(self):
        self.State = "Running"

    def SetFunction(self, Function):
        self.Function = Function


def ProgramLog(message, severity="error"):
    PROGRAM_LOG.append((str(message), severity))


def GetUnverifiedContext():
    return None


def event(*args, **kwargs):
    """extronlib.event(obj, 'Pressed'): a decorator that returns the function."""
    return lambda function: function


_MODELLED = {
    "extronlib": {"event": event},
    "extronlib.interface": {
        "EthernetClientInterface": EthernetClientInterface,
        "SerialInterface": SerialInterface,
        "EthernetServerInterfaceEx": EthernetServerInterfaceEx,
        "EthernetServerInterface": EthernetServerInterface,
    },
    "extronlib.system": {
        "Wait": Wait,
        "Timer": Timer,
        "ProgramLog": ProgramLog,
        "GetUnverifiedContext": GetUnverifiedContext,
    },
}

_EXML = "extronlib.standard.exml"


def _make_getattr(modname):
    """Unknown names: a lowercase one is a submodule (extronlib's are all
    lowercase - interface, system, device, ui ...), anything else a
    placeholder class."""
    def __getattr__(name):
        if name.startswith("__"):
            raise AttributeError(name)
        if name[:1].islower():
            return importlib.import_module(modname + "." + name)
        return type(name, (_Placeholder,), {})
    return __getattr__


class _Loader(importlib.abc.Loader):
    def create_module(self, spec):
        return None                 # default module creation

    def exec_module(self, module):
        name = module.__name__
        module.__path__ = []        # every extronlib module may have children
        if name == _EXML or name.startswith(_EXML + "."):
            # Extron's packaged ElementTree: stand in the standard library's.
            # No placeholder fallback here, so `from ...etree import
            # ElementTree` imports the child rather than getting a stub.
            rest = name[len(_EXML):]
            if rest.startswith(".etree."):
                real = importlib.import_module("xml.etree" + rest[len(".etree"):])
                module.__dict__.update({k: v for k, v in vars(real).items()
                                        if not k.startswith("__")})
            return
        for attr, value in _MODELLED.get(name, {}).items():
            setattr(module, attr, value)
        module.__getattr__ = _make_getattr(name)


class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "extronlib" or fullname.startswith("extronlib."):
            return importlib.machinery.ModuleSpec(fullname, _Loader(), is_package=True)
        return None


_FINDER = _Finder()


def install():
    """Make every `extronlib` import resolve to this stand-in."""
    if _FINDER not in sys.meta_path:
        sys.meta_path.insert(0, _FINDER)
    for name in [n for n in sys.modules if n == "extronlib" or n.startswith("extronlib.")]:
        del sys.modules[name]


def uninstall():
    if _FINDER in sys.meta_path:
        sys.meta_path.remove(_FINDER)
    for name in [n for n in sys.modules if n == "extronlib" or n.startswith("extronlib.")]:
        del sys.modules[name]
