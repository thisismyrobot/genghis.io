Code formatter
==============

Introduction
------------

The code formatter module takes a chunk of code, wrapping and formatting it
for execution back in the browser. This is usually called whenever the
contents of the IDE are updated.

Bootstrap
---------

Generic setup.

    >>> import json
    >>> import webtest

Create a webtest API app.

    >>> import api
    >>> api = webtest.TestApp(api.application)

Tests
-----

Format code
~~~~~~~~~~~

We need some code to format - this code loads the 'my_name' variable from
memory and says hello.

    >>> src = """
    ... @behaviour(priority=1)
    ... def friendly_person():
    ...     print 'Hello {}!'.format(memory.load('my_name', 'unsure'))
    ... """

And to prepare it in a json payload.

    >>> json_payload = json.dumps({'code': src})

Now we can format it.

    >>> formatted_code = json.loads(
    ...     api.post('/api/format', json_payload).body)['formatted_code']
    >>> print formatted_code
    # Look ...
    ...
            @behaviour(priority=1)
            def friendly_person():
                print 'Hello {}!'.format(memory.load('my_name', 'unsure'))
    ...
    sys.stdout.write(json.dumps(__output))
    <BLANKLINE>

Valid code
~~~~~~~~~~

The code returned is a valid block of Python, by the way. We'll add the memory
here though as that's inserted by JS in the real implementation. We're only
checking for the 'Hello bob!' here as we'll check the JSON output etc in other
tests.

    >>> import code
    >>> codelocals = {'__MEMORY': {'my_name': 'bob'}, '__BLACKLIST':[]}
    >>> codeobj = code.compile_command(formatted_code, '<string>', 'exec')
    >>> interpreter = code.InteractiveInterpreter(codelocals)
    >>> interpreter.runcode(codeobj)
    Hello bob!
    ...
