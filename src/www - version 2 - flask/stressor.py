import glob
import os
import random
import requests # pip install requests
import socketIO_client # pip install socketIO-client
import string
import time
import threading


DOMAIN = 'genghis.io'
#DOMAIN = 'localhost:8080'
DEPTH = 100 # 100 simultaneous users


def usecase_1():
    """ The basic use-case.

        A user loading main page, uploading a file, running code.
    
    """
    # Load the main page in the front-end
    requests.get('http://{}/'.format(DOMAIN))

    # Load the CSS in the front and back ends
    for js in map(os.path.basename, glob.glob(os.path.join('genghisio', 'static', 'css', '*.css'))):
        requests.get('http://{}/static/css/{}'.format(DOMAIN, js))

    # Load the main page in android webview
    requests.get('http://{}/android'.format(DOMAIN))

    # Load the JS in the front and back ends
    for js in map(os.path.basename, glob.glob(os.path.join('genghisio', 'static', 'js', '*.js'))):
        requests.get('http://{}/static/js/{}'.format(DOMAIN, js))

    # Load empythoned in the front-end
    requests.get('http://{}/static/emp/worker.js'.format(DOMAIN))
    requests.get('http://{}/static/emp/python.opt.js'.format(DOMAIN))

    # Get an API key
    sid = requests.get('http://{}/api/sid'.format(DOMAIN)).json()['sessionId']

    # Upload a file of 10KB of randomness
    requests.post('http://{}/api/file'.format(DOMAIN), files={
        'file': ('code.py',
                 ''.join(random.choice(
                        string.ascii_lowercase +
                        string.ascii_uppercase +
                        string.digits + ' ') for x in xrange(10000)))})

    # Load the connecting, then controller android pages
    requests.get('http://{}/android/connect/sphero'.format(DOMAIN))
    requests.get('http://{}/android/ready/sphero'.format(DOMAIN))

    # Start the websockets sequence
    class ApiNs(socketIO_client.BaseNamespace):
        pass

    sock = socketIO_client.SocketIO(DOMAIN)
    api_ns = sock.define(ApiNs, '/api')

    # Repeat for 10 minutes (1200 pings = 10 mins @ 2/second)
    for i in xrange(1200):
        # Emit the ping from the android webview
        api_ns.emit('ping', {
            'sessionId': sid,
            'inputs': [],
            'botId': 'sphero',
        })

        # Emit the response from the front-end
        api_ns.emit('control', {
            'sessionId': sid,
            'controls': [],
            'behaviours': {},
            'botId': 'sphero',
        })

        # Average ping time at moment
        time.sleep(0.5)


use_cases = (
    usecase_1,
)

if __name__ == '__main__':
    for use_case in use_cases:
        threads = []
        for d in xrange(DEPTH):
            threads.append(threading.Thread(target=use_case))
        for i, t in enumerate(threads):
            t.start()
            if i % 10 == 0:
                print 'Started', i
                time.sleep(1)
        for t in threads:
            t.join()
