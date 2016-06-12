"""

The API backend

Lots of easy to test things that support the API.

"""
import genghisio.drivers
import genghisio.controlqueue
import datetime
import hashlib
import operator
import os


def blacklist(controls):
    """ Returns the blacklist of behaviours from a controls queue.

        This is done by getting all the unique behaviour names from the
        currently queued controls.

    """
    return list(set(map(operator.itemgetter(3), controls)))


def format_file(code, header, footer, indent=8):
    """ Format a submitted source file for execution.

        Applies a header and footer and leading indent to the code.

    """
    src = header
    for line in code.split('\n'):
        src += '{}{}\n'.format(' ' * indent, line)
    src += footer
    return src


def new_sid(rand_bytes=1024):
    """ Returns a new session id.
    """
    return hashlib.sha1(os.urandom(rand_bytes)).hexdigest()


def queue_step(old_queue, new_controls, behaviour_map):
    """ Step the queue based on the new controls.

        Returns a tuple of a (new control, (debug messages,)).

        The new control may be None if queue is empty.

    """
    control = None
    debug = []

    # Update the queue with the new controls
    new_queue = genghisio.controlqueue.update(old_queue,
                                              new_controls,
                                              behaviour_map)

    # Init any new waits
    inspected = set()
    now = datetime.datetime.now()
    for i, item in enumerate(new_queue):

        # Only look at each behaviour once - aka only look at the first item
        # per behaviour.
        if item[2] in inspected:
            continue

        # Record each behaviour as we look at it, so we only look at it once.
        inspected.add(item[2])

        # Skip this behaviour if the first item isn't a wait
        if item[0] != '__wait__':
            continue

        # If the wait hasn't been initialised, do that now with a time that is
        # calculated as the expiry of the wait from now.
        if not isinstance(item[1], datetime.datetime):
            item[1] = new_queue[i][1] = now + datetime.timedelta(0, item[1])

    # Remove any expired waits
    i = 0
    while True:
        try:
            if new_queue[i][0] == '__wait__' and now > new_queue[i][1]:
                del(new_queue[i])
                continue
        except IndexError:
            # End of list
            break
        except TypeError:
            # When the new_queue[i][1] is not initialised
            pass
        i += 1

    # Process the queue, ignoring behaviours currently waiting, sending any
    # debug messages and hopefully ending up with a control
    waiting = set()
    i = 0
    while True:
        try:
            new_queue[i]
        except IndexError:
            break

        # If the head is a wait, mark behaviour as such and continue to next
        # item to look for a non-waiting behaviour.
        if new_queue[i][0] == '__wait__':
            waiting.add(new_queue[i][3])
            i += 1
            continue

        # If non-wait is from a behaviour that has already been marked as
        # waiting, continue to next item to look for a non-waiting behaviour.
        if new_queue[i][3] in waiting:
            i += 1
            continue

        # If the control is a debug message, consume it (adding to the debug
        # queue) and continue to next item to look for a control.
        if new_queue[i][0] == '__debug__':
            debug.append(new_queue.pop(i)[1])
            continue

        # We have a control if we're here, so we can remove it from the queue
        # and stop looping
        control = new_queue.pop(i)
        break

    return new_queue, control, tuple(debug)


def get_output(driver, control, args):
    """ Returns the serial string for a driver + control + args.
    """
    # Default to a safe 'stop' command
    ser_ctrl = genghisio.drivers.drivers[driver]['outputs']['stop']['func']()
    try:
        # Try to get the command
        ser_ctrl = genghisio.drivers.drivers[driver]['outputs'][control]['func'](*args)
    except:
        pass
    return ser_ctrl
