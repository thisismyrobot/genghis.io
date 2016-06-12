Development error helpers
=========================

Introduction
------------

Some testing of the helpers in place to provide clear and helpful errors to
the user when they make mistakes.

Bootstrap
---------

Import modules.

    >>> import api
    >>> import code
    >>> import json
    >>> import StringIO
    >>> import sys
    >>> import webtest

Create a webtest API app.

    >>> api = webtest.TestApp(api.application)

And a helper for executing code.

    >>> def exec_code(src, memory={}):
    ...     # Format the code
    ...     json_payload = json.dumps({'code': src})
    ...     formatted_code = json.loads(
    ...         api.post('/api/format', json_payload).body)['formatted_code']
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
    ...     # Return STDOUT
    ...     sys.stdout = old_stdout
    ...     return json.loads(buffer.getvalue())

Tests
-----

Behaviour decorator
~~~~~~~~~~~~~~~~~~~

Behaviour decorator needs a priority.

    >>> src = """
    ... @behaviour()
    ... def test():
    ...     pass
    ... """
    >>> print exec_code(src)['errors']
    Traceback (most recent call last):
    ...
    Exception: Behaviour decorator must have a priority - eg:
    <EXAMPLE>
    @behaviour(priority=1)
    </EXAMPLE>
    ...

The priority must be an integer.

    >>> src = """
    ... @behaviour(priority='no idea')
    ... def test():
    ...     pass
    ... """
    >>> print exec_code(src)['errors']
    Traceback (most recent call last):
    ...
    Exception: Behaviour priority must be an integer - eg:
    <EXAMPLE>
    @behaviour(priority=1)
    </EXAMPLE>
    ...

    >>> src = """
    ... @behaviour(priority=1.3)
    ... def test():
    ...     pass
    ... """
    >>> print exec_code(src)['errors']
    Traceback (most recent call last):
    ...
    Exception: Behaviour priority must be an integer - eg:
    <EXAMPLE>
    @behaviour(priority=1)
    </EXAMPLE>
    ...

You have to have at least one behaviour-decorated method.

    >>> src = """
    ... def test():
    ...     pass
    ... """
    >>> print exec_code(src)['errors']
    Traceback (most recent call last):
    ...
    Exception: At least one method must have a behaviour decorator - eg:
    <EXAMPLE>
    @behaviour(priority=1)
    def hello_world():
    ...
    </EXAMPLE>
    ...

Helper decorator
~~~~~~~~~~~~~~~~

Code can have helpers, they need to be decorated too though. This is what
happens if they are not.

    >>> src = """
    ... def debug_helper():
    ...     robot.move_forward(64)
    ...     debug('i help!')
    ...
    ... @behaviour(priority=6)
    ... def test():
    ...     debug_helper()
    ... """
    >>> print exec_code(src)['errors']
    Traceback (most recent call last):
    ...
    NameError: global name 'debug_helper' is not defined
    <BLANKLINE>

But by using the @helper decorator:

    >>> src = """
    ... @helper
    ... def debug_helper():
    ...     robot.move_forward(64)
    ...     debug('i help!')
    ...
    ... @behaviour(priority=6)
    ... def test():
    ...     debug_helper()
    ... """
    >>> result = exec_code(src)

We don't have any errors:

    >>> 'errors' in result.keys()
    False

It's important to note that the behaviour name is grabbed from the originating
behaviour.

    >>> print result['controls'][0]
    [u'move_forward', [64], u'test']

This works with nested methods (up to an unknown point...)

    >>> src = """
    ... @helper
    ... def move_helper(speed):
    ...     robot.move_forward(speed)
    ...
    ... @helper
    ... def debug_helper():
    ...     move_helper(64)
    ...     debug('i help!')
    ...
    ... @behaviour(priority=6)
    ... def test_2():
    ...     debug_helper()
    ... """
    >>> result = exec_code(src)

We don't have any errors:

    >>> 'errors' in result.keys()
    False

And the nested did too, and the control is correctly refereced to that top
level helper.

    >>> print result['controls'][0]
    [u'move_forward', [64], u'test_2']

Inter-behaviour calls
~~~~~~~~~~~~~~~~~~~~~

The developer can not make inter-behaviour calls.

    >>> src = """
    ... @behaviour(priority=6)
    ... def test_4():
    ...     debug('test 4')
    ...
    ... @behaviour(priority=6)
    ... def test_3():
    ...     test_4()
    ... """
    >>> result = exec_code(src)
    >>> print result['errors']
    Traceback (most recent call last):
    ...
    Exception: It looks like you are trying to call the 'test_4' behaviour method from the either another behaviour method or a helper.
    <BLANKLINE>
    This is not allowed as behaviours are called automatically.
    <BLANKLINE>

Nor can helpers call behaviours.

    >>> src = """
    ... @behaviour(priority=6)
    ... def test_4():
    ...     debug('test 4')
    ...
    ... @helper
    ... def my_little_helper():
    ...     test_4()
    ...
    ... @behaviour(priority=6)
    ... def test_3():
    ...     my_little_helper()
    ... """
    >>> result = exec_code(src)
    >>> print result['errors']
    Traceback (most recent call last):
    ...
    Exception: It looks like you are trying to call the 'test_4' behaviour method from the either another behaviour method or a helper.
    <BLANKLINE>
    This is not allowed as behaviours are called automatically.
    <BLANKLINE>

Debugging
~~~~~~~~~

To prevent errors, or to at least diagnose them, the user can use the debug
method. Debug statements push __debug__ controls into the control queue.

    >>> src = """
    ... @behaviour(priority=6)
    ... def test_moves():
    ...     robot.move_left(10)
    ...     debug('moving left')
    ...     robot.stop()
    ...     debug('stopping')
    ... """
    >>> result = exec_code(src)
    >>> print [(k,v,b) for k,v,b in result['controls']]
    [(u'move_left', [10], u'test_moves'), (u'__debug__', u'moving left', u'test_moves'), (u'stop', [], u'test_moves'), (u'__debug__', u'stopping', u'test_moves')]
