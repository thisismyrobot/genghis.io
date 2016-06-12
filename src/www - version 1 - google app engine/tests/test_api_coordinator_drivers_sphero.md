Driver: Sphero
==============

Introduction
------------

Tests of the methods available to the Sphero driver.

Bootstrap
---------

The driver id might be here as a global so we check - it will be a global if
we are doing a BallBot test - which runs this test with a different driver id.

    >>> try:
    ...     _ = driverid
    ... except NameError:
    ...     driverid = 'sphero'

Imports

    >>> import api
    >>> import code
    >>> import json
    >>> import StringIO
    >>> import sys
    >>> import webtest

The webtest app and a client_id.

    >>> app = webtest.TestApp(api.application)
    >>> client_id = '1234'

The client_id has an associated QR code.

    >>> qr = json.loads(app.get('/api/qr/{}'.format(client_id)).body)['qrcode']

Helper to execute code, saving the result into the server.

    >>> def execute_and_save(src, memory={}):
    ...     # Format the code
    ...     json_payload = json.dumps({'code': src})
    ...     formatted_code = json.loads(
    ...         app.post('/api/format', json_payload).body)['formatted_code']
    ...
    ...     # Compile it
    ...     codelocals = {'__MEMORY': memory, '__BLACKLIST': []}
    ...     codeobj = code.compile_command(formatted_code, '<string>', 'exec')
    ...     interpreter = code.InteractiveInterpreter(codelocals)
    ...
    ...     # Capture STDOUT
    ...     old_stdout = sys.stdout
    ...     sys.stdout = buffer = StringIO.StringIO()
    ...
    ...     # Run the code
    ...     interpreter.runcode(codeobj)
    ...
    ...     # Restore STDOUT
    ...     sys.stdout = old_stdout
    ...
    ...     json_data = json.loads(buffer.getvalue())
    ...
    ...     # Submit the result to the server
    ...     json_payload = json.dumps({
    ...         'controls': json_data['controls'],
    ...         'behaviours': json_data['behaviours'],
    ...     })
    ...     app.post('/api/record/{}'.format(client_id), json_payload)

Helper to get a control - behaves as the phone does and prints out the serial
data.

    >>> def get_control():
    ...     json_data = app.get('/api/ping/{}/{}'.format(qr, driverid)).body
    ...     print json.loads(json_data)['control']

Tests
-----

Movement
~~~~~~~~

Just a test of the simple commands for movement including stopping.

    >>> src = """
    ... @behaviour(priority=1)
    ... def stop():
    ...     robot.stop()
    ...     robot.move_forwards(64)
    ...     robot.move_right(64)
    ...     robot.move_backwards(64)
    ...     robot.move_left(64)
    ... """
    >>> execute_and_save(src)

Stop.

    >>> get_control()
    FFFE0230000500000001C7

Move forwards.

    >>> get_control()
    FFFE023000054000000187

Move right.

    >>> get_control()
    FFFE0230000540005A012D

Move backwards.

    >>> get_control()
    FFFE023000054000B401D3

Move left.

    >>> get_control()
    FFFE0230000540010E0178

No controls
~~~~~~~~~~~

Once we run out of controls we get an empty string for the serial data.

    >>> get_control()
    <BLANKLINE>
