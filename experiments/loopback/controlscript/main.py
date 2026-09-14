"""
Loopback run of the i20 ControlScript module on an Extron processor.

The camera is replaced by a PC running experiments/loopback/visca_listener.py.
On start this connects to that PC as if it were the i20, runs
loopback_steps.SEQUENCE one step every STEP_SECONDS, and writes every step,
every value read back, and every status change to the program log and trace.

Deploy in src/, beside:
    onebynd_camera_IV_CAM_I20_v1_0_0_0.py   (from experiments/skeleton_i20/out/)
    loopback_steps.py

Edit LISTENER_IP to the PC's address on the processor's network. See
experiments/loopback/README.md.
"""
import sys

from extronlib import Platform, Version
from extronlib.system import ProgramLog, Timer, Wait

from onebynd_camera_IV_CAM_I20_v1_0_0_0 import EthernetClass
import loopback_steps

LISTENER_IP = '192.168.254.10'     # the PC running visca_listener.py
LISTENER_PORT = 5500
STEP_SECONDS = 1.5


def log(message):
    print(message)
    ProgramLog(message, 'info')


log('loopback: ControlScript %s %s, Python %s'
    % (Platform(), Version(), sys.version.split()[0]))

cam = EthernetClass(LISTENER_IP, LISTENER_PORT)


def status_changed(command, value, qualifier):
    log('loopback: status %s = %r %s' % (command, value, qualifier or ''))


for _command in cam.Commands:
    cam.SubscribeStatus(_command, None, status_changed)

steps = list(loopback_steps.SEQUENCE)
position = [0]


def run_step(timer, count):
    i = position[0]
    if i >= len(steps):
        timer.Stop()
        log('loopback: sequence complete, %d steps' % len(steps))
        return
    position[0] = i + 1
    kind, command, value, qualifier, note = steps[i]
    log('loopback: step %d/%d %s %s %r %r (%s)'
        % (i + 1, len(steps), kind, command, value, qualifier, note))
    try:
        if kind == 'Set':
            cam.Set(command, value, qualifier)
        else:
            cam.Update(command, qualifier)
            log('loopback: read %s %s = %r'
                % (command, qualifier or '', cam.ReadStatus(command, qualifier)))
    except Exception as e:
        log('loopback: step %d raised %s: %s' % (i + 1, type(e).__name__, e))


def start():
    result = cam.Connect(5)
    log('loopback: connect %s:%d -> %s' % (LISTENER_IP, LISTENER_PORT, result))
    if 'Connected' not in result:
        Wait(5, start)
        return
    Timer(STEP_SECONDS, run_step)


start()
