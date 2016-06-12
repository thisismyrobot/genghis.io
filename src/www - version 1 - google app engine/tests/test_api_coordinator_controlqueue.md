Coordinator control queue
=========================

Introduction
------------

The coordinator module's control queue manages the queue of controls stored on
the server.

Bootstrap
---------

Imports and a working control queue.

    >>> import api.coordinator.controlqueue
    >>> controls_queue = []

A helper method.

    >>> def update(new_controls, behaviour_map):
    ...     global controls_queue
    ...     controls_queue = api.coordinator.controlqueue.update(
    ...         controls_queue, new_controls, behaviour_map)
    ...     return controls_queue

Tests
-----

Basic ordering
~~~~~~~~~~~~~~

We need some basic controls to submit.

    >>> controls = [['move_left', 3, 'behaviour_1'],
    ...             ['stop', None, 'behaviour_2']]

And a priority for each behaviour.

    >>> behaviour_map = {
    ...     'behaviour_1': 2,
    ...     'behaviour_2': 1,
    ...     'behaviour_3': 3,
    ...     'behaviour_4': 0,
    ... }

Now we can update the currently empty queue with this info. Of note is the
fact that the stop went to the front due to its higher priority.

    >>> update(controls, behaviour_map)
    [('stop', None, 1, 'behaviour_2'), ('move_left', 3, 2, 'behaviour_1')]

Limited repetition
~~~~~~~~~~~~~~~~~~

We look for the same control entering the queue but with a higher priority. In
this case we delete the lower priority control. Here we'll add a P0
'move_left:3' and it will move to the front, removing the same control from
the tail.

    >>> controls = [['move_left', 3, 'behaviour_4']]
    >>> _ = update(controls, behaviour_map)
    >>> [(k, v, p) for (k, v, p, _) in controls_queue]
    [('move_left', 3, 0), ('stop', None, 1)]

We also stop new controls for an existing behaviour, per update. We can't,
currently, add any new controls for behaviour 4.

    >>> controls = [['move_forward', 7, 'behaviour_4']]
    >>> _ = update(controls, behaviour_map)
    >>> [(k, v, p) for (k, v, p, _) in controls_queue]
    [('move_left', 3, 0), ('stop', None, 1)]

But if we remove the existing behaviour 4 control we can.

    >>> controls_queue = controls_queue[1:]
    >>> [(k, v, p) for (k, v, p, _) in controls_queue]
    [('stop', None, 1)]

The move_forward is at the front as behaviour 4 is a P0.

    >>> _ = update(controls, behaviour_map)
    >>> [(k, v, p) for (k, v, p, _) in controls_queue]
    [('move_forward', 7, 0), ('stop', None, 1)]
