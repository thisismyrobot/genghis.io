"""

    Definitions of the drivers.

    Drivers can call helpers out of the driver-specific helper modules in the
    helpers package.

"""
from helpers import sphero


drivers = {
    'common': {
        'name': 'Common controls',
        'outputs': {
            'wait': {
                'args': ((int, 1, 10),),
                'func': lambda time: None
            },
        },
    },
    'sphero': {
        'name': 'Sphero 2.0',
        'outputs': {
            'move_forwards': {
                'args': ((int, 1, 64),),
                'func': lambda speed: sphero.SerialString.move(0, speed),
            },
            'move_left': {
                'args': ((int, 1, 64),),
                'func': lambda speed: sphero.SerialString.move(270, speed),
            },
            'move_backwards': {
                'args': ((int, 1, 64),),
                'func': lambda speed: sphero.SerialString.move(180, speed),
            },
            'move_right': {
                'args': ((int, 1, 64),),
                'func': lambda speed: sphero.SerialString.move(90, speed),
            },
            'stop': {
                'args': (),
                'func': lambda: sphero.SerialString.stop()
            },
            'set_colour': {
                'args': ((int, 0, 255), (int, 0, 255), (int, 0, 255)),
                'func': lambda red, green, blue: None,
            },
        },
    },
}

# Add the test driver as a copy of the Sphero driver
drivers['ballbot'] = drivers['sphero']
drivers['ballbot']['name'] = 'BallBot'
