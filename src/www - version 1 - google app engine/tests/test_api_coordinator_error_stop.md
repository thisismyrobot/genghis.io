Emergency stop
==============

Introduction
------------

If there is an error in the code, the control queue generates an emergency
stop command. This replaces the current contents of the queue. This would
normally be called by the javascript wrapping empythoned.

Bootstrap
---------

Imports and a working control queue.

    >>> import api
    >>> import json
    >>> import webtest

Create a webtest API app.

    >>> app = webtest.TestApp(api.application)

Create a client_id + QR code + set a driver ID.

    >>> client_id = '1234'
    >>> driverid = 'sphero'
    >>> qr = json.loads(app.get('/api/qr/{}'.format(client_id)).body)['qrcode']

And pre-populate some controls.

    >>> controls = [['move_left', [64], 'behaviour_1'],
    ...             ['move_right', [64], 'behaviour_1'],
    ...             ['move_forwards', [64], 'behaviour_1'],
    ...             ['move_backwards', [64], 'behaviour_1']]
    >>> behaviour_map = {
    ...     'behaviour_1': 3,
    ... }
    >>> json_payload = json.dumps({
    ...     'controls': controls,
    ...     'behaviours': behaviour_map, 
    ... })
    >>> _ = app.post('/api/record/{}'.format(client_id), json_payload)

Tests
-----

Stop command insertion
~~~~~~~~~~~~~~~~~~~~~~

The stop command is inserted via a GET to /api/stop/[client_id]/[driverid].
Currently, we can grab the head of the queue (move_left) via the normal Ping.

    >>> json.loads(app.get('/api/ping/{}/{}'.format(qr, driverid)).body)['control']
    u'FFFE0230000540010E0178'

Normally doing another ping would trigger a move_right, but we'll insert a
stop due to a hypothetical error in the code that is detected by the client
JS.

    >>> _ = app.get('/api/stop/{}/{}'.format(client_id, driverid))

Now, when we ping, we'll get a stop command.

    >>> json.loads(app.get('/api/ping/{}/{}'.format(qr, driverid)).body)['control']
    u'FFFE0230000500000001C7'
