Driver: BallBot
===============

Introduction
------------

Tests of the methods available to the BallBot driver - the driver that can be
used to test Sphero driver code locally. This test should attempt to be as
similar to the test_api_coordinator_drivers_sphero tests as possible with the
exception of the driverid being 'ballbot'.

Sphero-compatibility
--------------------

We're going to cheat a bit and call the Sphero test with an extra global to
override the driverid to 'ballbot'. If the test fails an exception will be
thrown.

    >>> import os
    >>> testpath = os.path.join(
    ...     os.getcwd(), 'www', 'tests',
    ...     'test_api_coordinator_drivers_sphero.md')

    >>> import doctest
    >>> _ = doctest.testfile(testpath,
    ...                      raise_on_error=True,
    ...                      optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
    ...                      extraglobs={
    ...     'driverid': 'ballbot',
    ... })

JSON payload
------------

The JSON from the bot includes the passed in command to make it easy to do a
web bot (otherwise we'd have to parse the serial string again...):

Setup
~~~~~

    >>> import api
    >>> import json
    >>> import webtest
    >>> app = webtest.TestApp(api.application)
    >>> client_id = '1234'
    >>> qr = json.loads(app.get('/api/qr/{}'.format(client_id)).body)['qrcode']

Record some controls
~~~~~~~~~~~~~~~~~~~~

    >>> json_payload = json.dumps({
    ...     'controls': [['move_forwards', [64], u'test']],
    ...     'behaviours': {'test': 1},
    ... })
    >>> _ = app.post('/api/record/{}'.format(client_id), json_payload)

Test
~~~~

    >>> json.loads(app.get('/api/ping/{}/ballbot'.format(qr)).body)['cmdecho']
    [u'move_forwards', [64]]
