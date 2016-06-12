Empythoned tests - Random
=========================

Introduction
------------

Random is a bit funny in the helper - the module-level methods don't work. So
it's been patched a bit. This tests to make sure the patch is ok.

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

    >>> app = webtest.TestApp(api.application)

And a helper for executing code.

    >>> def exec_code(src, memory={}):
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
    ...     # Return STDOUT
    ...     sys.stdout = old_stdout
    ...     return json.loads(buffer.getvalue())

Tests
-----

This just checks that the random module still works...

    >>> src = """
    ... @behaviour(priority=1)
    ... def test():
    ...     random.seed()
    ...     debug(random.choice(['7', '7']))
    ... """
    >>> print exec_code(src)['controls'][0][1]
    7
