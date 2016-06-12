API Backend
===========

Tests of the API backend.

Setup
-----

    >>> import genghisio.api.backend as backend
    >>> import time

Queueing step
-------------

The queue step handles all the fundamental logic around adding new controls
and retrieving the next control to execute. This is where the core behaviour-
based control is implemented.

It can handle no initial or new controls, returning no controls, a None head
and no debug messages.

    >>> backend.queue_step(
    ...     [],
    ...     [],
    ...     {},
    ... )
    ([], None, ())

It gracefully handles missing behaviour mappings :)

    >>> backend.queue_step(
    ...     [],
    ...     [
    ...         ['move_forwards', [32], 'test_behav'],
    ...     ],
    ...     {},
    ... )
    ([], None, ())

It can add controls where there weren't any before.

    >>> backend.queue_step(
    ...     [],
    ...     [
    ...         ['move_forwards', [32], 'test_behav'],
    ...     ],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )
    ([], ('move_forwards', [32], 1, 'test_behav'), ())

It respects the order of controls of the same priority.

    >>> backend.queue_step(
    ...     [],
    ...     [
    ...         ['move_forwards', [32], 'test_behav'],
    ...         ['move_left', [7], 'test_behav2'],
    ...     ],
    ...     {
    ...         'test_behav': 1,
    ...         'test_behav2': 1,
    ...     },
    ... )
    ([('move_left', [7], 1, 'test_behav2')], ('move_forwards', [32], 1, 'test_behav'), ())

And uses the priority mapping to manage order - test_behav2 is higher priority
so it's control goes first.

    >>> backend.queue_step(
    ...     [],
    ...     [
    ...         ['move_forwards', [32], 'test_behav'],
    ...         ['move_left', [7], 'test_behav2'],
    ...     ],
    ...     {
    ...         'test_behav': 2,
    ...         'test_behav2': 1,
    ...     },
    ... )
    ([('move_forwards', [32], 2, 'test_behav')], ('move_left', [7], 1, 'test_behav2'), ())

The queue is consumed as it is processed, even without any new controls.

    >>> backend.queue_step(
    ...     [('move_forwards', [32], 1, 'test_behav')],
    ...     [],
    ...     {},
    ... )
    ([], ('move_forwards', [32], 1, 'test_behav'), ())

All debug messages are processed until the first control, and queue like
controls.

    >>> backend.queue_step(
    ...     [('__debug__', 'hi', 1, 'test_behav'), ('move_forwards', [32], 1, 'test_behav')],
    ...     [
    ...         ['__debug__', 'hello', 'test_behav'],
    ...     ],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )
    ([('__debug__', 'hello', 1, 'test_behav')], ('move_forwards', [32], 1, 'test_behav'), ('hi',))

    >>> backend.queue_step(
    ...     [('__debug__', 'hello', 1, 'test_behav')],
    ...     [],
    ...     {},
    ... )
    ([], None, ('hello',))

You can insert duplicates.

    >>> backend.queue_step(
    ...     [('move_left', [16], 1, 'test_behav')],
    ...     [
    ...         ['move_forwards', [32], 'test_behav'],
    ...         ['move_forwards', [64], 'test_behav'],
    ...     ],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )[0]
    [('move_forwards', [32], 1, 'test_behav'), ('move_forwards', [64], 1, 'test_behav')]

Waits are handled in a special way - they block any other controls for that
behaviour and and try to find the next available control.

    >>> backend.queue_step(
    ...     [('move_left', [16], 1, 'test_behav'), ['__wait__', 1, 1, 'test_behav']],
    ...     [],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )
    ([['__wait__', 1, 1, 'test_behav']], ('move_left', [16], 1, 'test_behav'), ())

When a behaviour is first seen at the front of the queue, it is converted to a
datetime.

    >>> new_q = backend.queue_step(
    ...     [
    ...         ['__wait__', 1, 1, 'test_behav'],
    ...         ['__wait__', 3, 1, 'test_behav'],
    ...     ],
    ...     [],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )[0]
    >>> new_q
    [['__wait__', datetime.datetime(...), 1, 'test_behav'], ['__wait__', 3, 1, 'test_behav']]

This only happens once.

    >>> backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )[0] == new_q
    True

A wait can expire immediately.

    >>> backend.queue_step(
    ...     [
    ...         ['__wait__', -4, 1, 'test_behav'],
    ...         ['move_forwards', [28], 1, 'test_behav'],
    ...     ],
    ...     [],
    ...     {
    ...         'test_behav': 1,
    ...     },
    ... )[1]
    ['move_forwards', [28], 1, 'test_behav']

A complicated example of handover between behaviours. The higher priority
behaviour runs until a wait causes it to pause, promoting the next behaviour.

    >>> new_q, ctrl = backend.queue_step(
    ...     [
    ...         ['move_forwards', [10], 1, 'test_behav1'],
    ...         ['move_left', [12], 1, 'test_behav1'],
    ...         ['__wait__', 1, 1, 'test_behav1'],
    ...         ['move_backwards', [5], 1, 'test_behav1'],
    ...         ['spin', [], 2, 'test_behav2'],
    ...         ['__wait__', 2, 2, 'test_behav2'],
    ...         ['flash_lights', [], 3, 'test_behav3'],
    ...     ],
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl
    ['move_forwards', [10], 1, 'test_behav1']

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl
    ['move_left', [12], 1, 'test_behav1']

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl
    ['spin', [], 2, 'test_behav2']

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl
    ['flash_lights', [], 3, 'test_behav3']

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl is None
    True

    >>> time.sleep(1)

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl
    ['move_backwards', [5], 1, 'test_behav1']

    >>> new_q, ctrl = backend.queue_step(
    ...     new_q,
    ...     [],
    ...     {
    ...         'test_behav1': 1,
    ...         'test_behav2': 2,
    ...         'test_behav3': 3,
    ...     },
    ... )[:2]

    >>> ctrl is None
    True

    >>> new_q
    [['__wait__', datetime.datetime(...), 2, 'test_behav2']]
