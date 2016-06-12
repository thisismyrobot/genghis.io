import json
import random
import sys
import time

# Catches for non-std modules
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    sys.stderr.write("Error: Requires pySerial from http://pyserial.sourceforge.net/\n")
    sys.exit(1)

# Catches for non-std modules
try:
    import requests
except ImportError:
    sys.stderr.write("Error: Requires Requests from http://docs.python-requests.org/en/latest/\n")
    sys.exit(1)

### Settings

# The sphero BT UID
UUID = '00001101-0000-1000-8000-00805F9B34FB'
DOMAIN = 'http://localhost:8080'
#DOMAIN = 'https://pytoyapp.appspot.com'
PINGURL = '{}/ajax/ping/{}'
IDEURL = '{}/ajax/ide/update'
STARTURL = '{}/ajax/control/{}/start'
DEVID = 'sphero'
SID = ''.join([str(random.randint(0,9)) for r in range(20)])
CODE = """

def behaviour_test_square():
    sphero.set_move_forward()
    sphero.wait(1)
    sphero.set_stop()
    sphero.wait(2)
    sphero.set_move_left()
    sphero.wait(1)
    sphero.set_stop()
    sphero.wait(2)
    sphero.set_move_back()
    sphero.wait(1)
    sphero.set_stop()
    sphero.wait(2)
    sphero.set_move_right()
    sphero.wait(1)
    sphero.set_stop()
    sphero.wait(2)

"""


### Helpers

def setup():
    # Upload/update the code
    r = requests.post(IDEURL.format(DOMAIN), data={
        'sessionid': SID,
        'src': CODE,
        'driver_id': DEVID,
    })

    if r.status_code != 200:
        sys.stderr.write("Error: Failed to upload code\n")
        sys.exit(1)

    # Start the code
    r = requests.get(STARTURL.format(DOMAIN, SID))

    if r.status_code != 200:
        sys.stderr.write("Error: Failed to start code\n")
        sys.exit(1)


def ping():
    """ Perform a ping, returning the result.
    """
    # Do the ping
    r = requests.post(PINGURL.format(DOMAIN, SID), data=json.dumps({}))
    if r.status_code != 200:
        sys.stderr.write("Error: Failed to do ping\n")
        sys.exit(1)
    return r.text

### Main code

if __name__ == '__main__':
    # Get the Sphero's serial port
    try:
        sph_com = serial.tools.list_ports.grep(UUID).next()[0]
        sph_ser = serial.Serial(sph_com, 115200)
    except:
        sys.stderr.write("Error: No Sphero connected\n")
        sys.stderr.write("Check for OS Bluetooth connection request - use pin 1234\n")
        sys.exit(1)

    # Start pinging
    setup()

    while True:
        try:
            data = json.loads(ping())
            print sorted(data.items())
            control = data['control']
            if control != {}:
                sph_ser.write(control.decode('hex'))
            time.sleep(0.1)
        except:
            # Stop
            print 'Stopping...'
            sph_ser.write('FFFE0230000500000001C7'.decode('hex'))
            sys.exit(0)
