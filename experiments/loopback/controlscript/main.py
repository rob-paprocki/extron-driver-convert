"""
Loopback console for the i20 ControlScript module, on an Extron processor.

The camera is replaced by a PC running experiments/loopback/run_loopback.py
(or visca_listener.py). This program serves a command console on TCP
CONSOLE_PORT; the PC connects to it, tells the module to target the PC itself,
and then sends every Set / Update / ReadStatus the test needs. Nothing to edit
per network: the camera target defaults to whichever PC asks.

Deploy in src/, beside:
    console_core.py
    onebynd_camera_IV_CAM_I20_v1_0_0_0.py   (from experiments/skeleton_i20/out/)

Protocol and requests: console_core.py. Written to Python 3.5 syntax, so the
same file runs on xi and non-xi processors.
"""
import queue
import sys
import threading

from extronlib import Platform, Version, event
from extronlib.interface import EthernetServerInterfaceEx
from extronlib.system import ProgramLog

from onebynd_camera_IV_CAM_I20_v1_0_0_0 import EthernetClass
from console_core import Console, encode

CONSOLE_PORT = 5600
CAMERA_PORT = 5500

INFO = {'platform': Platform(), 'version': Version(), 'python': sys.version.split()[0],
        'console_port': CONSOLE_PORT}
ProgramLog('loopback console: ControlScript %s %s, Python %s'
           % (INFO['platform'], INFO['version'], INFO['python']), 'info')

server = EthernetServerInterfaceEx(CONSOLE_PORT, 'TCP', 'Any', 4)
clients = {}                    # (ip, port) -> [client, unconsumed bytes]
clients_lock = threading.Lock()
requests = queue.Queue()


def client_key(client):
    return (client.IPAddress, client.ServicePort)


def broadcast(obj):
    data = encode(obj)
    with clients_lock:
        targets = [entry[0] for entry in clients.values()]
    for client in targets:
        try:
            client.Send(data)
        except Exception as e:
            print('loopback console: send to %s failed: %s' % (client.IPAddress, e))


console = Console(EthernetClass, broadcast, CAMERA_PORT, INFO)


def serve_requests():
    # Requests run here, not in the ReceiveData handler, because the module's
    # Set/Update call SendAndWait, which must not run inside a ReceiveData event.
    while True:
        client, line = requests.get()
        reply = console.handle(line, client.IPAddress)
        print('loopback console: %s -> ok=%s' % (line[:120], reply.get('ok')))
        try:
            client.Send(encode(reply))
        except Exception as e:
            print('loopback console: reply to %s failed: %s' % (client.IPAddress, e))


threading.Thread(target=serve_requests, daemon=True).start()


@event(server, 'Connected')
def client_connected(client, state):
    with clients_lock:
        clients[client_key(client)] = [client, b'']
    print('loopback console: %s connected' % client.IPAddress)


@event(server, 'Disconnected')
def client_disconnected(client, state):
    with clients_lock:
        clients.pop(client_key(client), None)
    print('loopback console: %s disconnected' % client.IPAddress)


@event(server, 'ReceiveData')
def client_data(client, data):
    with clients_lock:
        entry = clients.setdefault(client_key(client), [client, b''])
        entry[1] += data
        lines = entry[1].split(b'\n')
        entry[1] = lines.pop()
    for raw in lines:
        raw = raw.strip()
        if raw:
            requests.put((client, raw.decode('utf-8', 'replace')))


result = server.StartListen()
ProgramLog('loopback console: TCP %d -> %s' % (CONSOLE_PORT, result), 'info')
