"""
The command sequence main.py runs on the processor.

Kept free of extronlib so the repo's tests can import it and check, offline,
that driving the module through these steps puts every PROTOCOL T3 wire string
on the wire in order. Deploy it beside main.py.

Each step is (kind, command, value, qualifier, note); kind is 'Set' or 'Update'.
"""

T3 = [
    ('Set', 'Power', 'On', None, 'T3 1'),
    ('Set', 'Preset', 1, {'Action': 'Recall'}, 'T3 2'),
    ('Set', 'Zoom', 'Tele', {'Speed': 5}, 'T3 3'),
    ('Set', 'TrackingFraming', 'Start', None, 'T3 4'),
    ('Update', 'TrackingFraming', None, None, 'T3 5, expect Start'),
    ('Set', 'TrackingFraming', 'Stop', None, 'T3 6'),
    ('Update', 'TrackingFraming', None, None, 'T3 7, expect Stop'),
    ('Set', 'ZoomPosition', 6699, {'Speed': 3}, 'T3 8'),
    ('Set', 'FreezeFrame', 'On', None, 'T3 9'),
    ('Set', 'FreezeFrame', 'Off', None, 'T3 9'),
    ('Set', 'IndicatorLight', 'Full', {'Color': 'Red', 'Brightness': 'Bright'}, 'T3 10'),
    ('Set', 'IndicatorLight', 'Half', {'Color': 'Green', 'Brightness': 'Dim'}, 'T3 11'),
    ('Set', 'IndicatorLight', 'None', None, 'T3 12'),
    ('Set', 'TrackingProfile', 2, None, 'T3 13'),
    ('Set', 'CameraOutput', 2, None, 'T3 14'),
    ('Set', 'IntelligentSwitching', 'Resume', None, 'T3 15'),
    ('Set', 'IntelligentSwitching', 'Pause', None, 'T3 16'),
    ('Set', 'GroupTracking', 'Enable', None, 'T3b 1'),
    ('Set', 'PresenterTracking', 'Enable', None, 'T3b 2'),
]

# The composed commands at the ends of the ranges GC renders, then read back.
EDGES = [
    ('Set', 'PanTiltAngle', None,
     {'Pan Speed': 1, 'Tilt Speed': 1, 'Pan': -2448, 'Tilt': -1296}, 'edge, low'),
    ('Update', 'PanAngleStatus', None, None, 'edge, expect -2448'),
    ('Update', 'TiltAngleStatus', None, None, 'edge, expect -1296'),
    ('Set', 'PanTiltAngle', None,
     {'Pan Speed': 24, 'Tilt Speed': 20, 'Pan': 2448, 'Tilt': 1296}, 'edge, high'),
    ('Update', 'PanAngleStatus', None, None, 'edge, expect 2448'),
    ('Update', 'TiltAngleStatus', None, None, 'edge, expect 1296'),
    ('Set', 'ZoomPosition', 0, {'Speed': 0}, 'edge, low'),
    ('Set', 'ZoomPosition', 16384, {'Speed': 7}, 'edge, high'),
    ('Update', 'ZoomPosition', None, None, 'edge, expect 16384'),
    ('Set', 'CameraOutput', 5, None, 'edge'),
    ('Update', 'CameraOutput', None, None, 'edge, expect 5'),
]

# Every command that supports Update(), once each.
POLLS = [('Update', c, None, None, 'poll') for c in (
    'Power', 'AutoExposure', 'AutoFocus', 'Backlight', 'WhiteBalance',
    'FreezeFrame', 'TrackingFraming')] + [
    ('Update', 'CameraConnectionStatus', None, {'Camera': n}, 'poll')
    for n in (2, 3, 4, 5)]

SEQUENCE = T3 + EDGES + POLLS
