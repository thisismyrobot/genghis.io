Demo code API
=============

Introduction
------------

There is a simple API that returns JSON-wrapped code examples.

Bootstrap
---------

Generic setup.

    >>> import json
    >>> import webtest

Create a webtest API app.

    >>> import api
    >>> app = webtest.TestApp(api.application)

And a helper.

    >>> API_URL = '/api/ide/code'
    >>> def get_code(driver_id=None, code_id=None):
    ...     params = {}
    ...     if driver_id is not None:
    ...         params['driver'] = driver_id
    ...     if code_id is not None:
    ...         params['code'] = code_id
    ...     return json.loads(app.get(API_URL, params).body)['code']

Tests
-----

Hello world
~~~~~~~~~~~

If you don't select a driver id or code id, you will receive the very basic
'Hello World' application.

    >>> print get_code(),
    """
        A basic Hello World
    """
    @behaviour(priority=1)
    def hello_world():
        debug('Hello world!')

Generic code
~~~~~~~~~~~~

If you only have a code id you can load some other generic code.

    >>> print get_code(None, 'counter'),
    """
        A basic counter
    """
    @behaviour(priority=1)
    def counter():
        # Load the counter from memory, set it to zero if first time
        counter_value = memory.load('counter', 0)
    <BLANKLINE>
        # Print out the value of the counter
        debug(counter_value)
    <BLANKLINE>
        # Increment the counter by 1
        counter_value = counter_value + 1
    <BLANKLINE>
        # Save it back in the memory
        memory.save('counter', counter_value)

Driver defaults
~~~~~~~~~~~~~~~

If you only have the driver id you get a default example - this will happen at
page load.

    >>> print get_code('sphero'),
    """
        Drive in a square
    """
    @behaviour(priority=1)
    def drive_square():
        robot.move_forwards(64)
        robot.stop()
        robot.move_right(64)
        robot.stop()
        robot.move_backwards(64)
        robot.stop()
        robot.move_left(64)
        robot.stop()

Driver and code id
~~~~~~~~~~~~~~~~~~

There are of course multiple examples per driver.

    >>> print get_code('sphero', 'square'),
    """
        Drive in a square
    """
    @behaviour(priority=1)
    def drive_square():
        robot.move_forwards(64)
        robot.stop()
        robot.move_right(64)
        robot.stop()
        robot.move_backwards(64)
        robot.stop()
        robot.move_left(64)
        robot.stop()

Example code execution
~~~~~~~~~~~~~~~~~~~~~~

For each of the examples it would be nice to run them a lot of times to test
they work... We need a helper first.

    >>> import code
    >>> import sys
    >>> import StringIO

    >>> memory = {}
    >>> def test(example_src, iterations=20):
    ...     global memory
    ...
    ...     # Format the code
    ...     json_payload = json.dumps({'code': example_src})
    ...     formatted_code = json.loads(
    ...         app.post('/api/format', json_payload).body)['formatted_code']
    ...
    ...     # Compile it
    ...     codeobj = code.compile_command(formatted_code, '<string>', 'exec')
    ...     for i in range(iterations):
    ...         codelocals = {'__MEMORY': memory, '__BLACKLIST': []}
    ...         interpreter = code.InteractiveInterpreter(codelocals)
    ...
    ...         # Capture STDOUT
    ...         old_stdout = sys.stdout
    ...         sys.stdout = buffer = StringIO.StringIO()
    ...
    ...         # Execute it
    ...         interpreter.runcode(codeobj)
    ...
    ...         # Restore STDOUT
    ...         sys.stdout = old_stdout
    ...     
    ...         # Grab the JSON - parse the memory/errors
    ...         json_data = json.loads(buffer.getvalue())
    ...         memory = json_data['memory']
    ...
    ...         # Print the errors to fail the test
    ...         if 'errors' in json_data.keys():
    ...             print json_data['errors']
    ...             return

Just to sanity-check the tester...

    >>> src = """
    ... print 'hello'
    ... """
    >>> test(src)
    Traceback (most recent call last):
    ...
    ValueError: No JSON object could be decoded

    >>> src = """
    ... @behaviour(priority=1)
    ... def div():
    ...     x = 1 / 0
    ... """
    >>> test(src, 1)
    Traceback (most recent call last):
    ...
    ZeroDivisionError: integer division or modulo by zero
    <BLANKLINE>

    >>> src = """
    ... @behaviour(priority=1)
    ... def memory():
    ...     i = memory.load('test', 0)
    ...     i += 1
    ...     memory.save('test', i)
    ... """
    >>> test(src, 7)
    >>> memory
    {u'test': 7}

Now we can test the code

    >>> import api.ide.code
    >>> memory = {}
    >>> for (driverid, codeid) in api.ide.code.EXAMPLE_DATA.keys():
    ...     # Get the code
    ...     example_src = get_code(driverid, codeid)
    ...
    ...     # Test the code
    ...     test(example_src)

We know we save something to memory in at least one of the examples.

    >>> len(memory) > 0
    True

Code examples per driver
~~~~~~~~~~~~~~~~~~~~~~~~

An API helper returns a summary of the examples for a driver. It returns non-driver
examples if no driverid is passed in.

    >>> data = json.loads(app.get('/api/ide/code/').body)['examples']

We have at least one non-driver example

    >>> len(data) > 0
    True

And it is made up of four bits of data

    >>> len(data[0])
    4

If you select a drive (eg sphero), you get different examples

    >>> sphero_data = json.loads(app.get('/api/ide/code/sphero').body)['examples']
    >>> data == sphero_data
    False

    >>> len(sphero_data) > 0
    True

    >>> len(sphero_data[0])
    4
