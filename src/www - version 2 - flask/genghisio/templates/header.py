# Look after the globals - we are inserting helpers here and we want to remove
# them regularly so that if someone removes an @helper decorator we can catch
# and error predictably.
try:
    for name in __helper_cache:
        if name in globals().keys():
            del globals()[name]
    __helper_cache = set()
except NameError:
    __helper_cache = set()


# Required imports
import json
import random
import sys


# This becomes the json with the output control/error
__output = {'controls': []}

# This holds any exceptions generated
__expt = None

# A map of behaviours and priorities
__behaviours = {}

# Fixes for Random - copied from random.py as the module-level functions are
# not exported when used in empythoned...
__random = random.Random()
methods = filter(lambda method: method.lower() == method, random.__all__)
for method in methods:
    setattr(random, method, getattr(__random, method))

# Helpers
def debug(message):
    """ Allows for in-code debugging.

        Inserts the message as a 'control' and the control is sent to the user
        via websockets instead of to the phone. This is then displayed for the
        user.

    """
    calling_behaviour = Robot._get_behaviour(__behaviours)
    __output['controls'].append(('__debug__', message, calling_behaviour))


def wait(seconds):
    """ Causes the behaviour to wait for a period of time in seconds.
    """
    calling_behaviour = Robot._get_behaviour(__behaviours)
    __output['controls'].append(('__wait__', seconds, calling_behaviour))


def behaviour(priority=None):
    """ Decorator for methods that are behaviours - records the names in a
        set for later calling.
    """
    # Priority is required
    if priority is None:
        raise Exception(
            'Behaviour decorator must have a priority - eg:\n' + \
            '<EXAMPLE>\n' + \
            '@behaviour(priority=1)\n' + \
            '</EXAMPLE>')

    # Priority must be an integer
    try:
        if int(priority) != priority:
            raise Exception
    except:
        raise Exception(
            'Behaviour priority must be an integer - eg:\n' + \
            '<EXAMPLE>\n' + \
            '@behaviour(priority=1)\n' + \
            '</EXAMPLE>')

    def wrap(behaviour_method):
        __behaviours[behaviour_method.__name__] = priority
        def wrapped(*args):
            behaviour_method()
        return staticmethod(wrapped)
    return wrap

def helper(helper_function):
    """ Decorator for methods that are helpers in the code itself.

        This decorator inserts the wrapped method into globals().

    """
    globals()[helper_function.__name__] = helper_function
    __helper_cache.add(helper_function.__name__)
    return helper_function


# Main class
class Robot(object):
    def __init__(self, outputdict, behaviours):
        self._outputdict = outputdict
        self._behaviours = behaviours

    def __add(self, key, args, calling_behaviour):
        """ Add entries to the outputdict.
        """
        self._outputdict['controls'].append((key, args, calling_behaviour))

    def __getattr__(self, key):
        """ Intercept attribute access when not matching something that is
            defined on the driver. This gives us the 'set_' behaviour we want.
        """
        # Try to Work out the calling behaviour
        calling_behaviour = Robot._get_behaviour(self._behaviours)

        # Look for 'set_*', 'move_' or 'stop' calls
        if key.startswith('set_') or key.startswith('move_') or key == 'stop':

            # Return the 'key' object with a callable attached. The callable
            # maps to self.__add(key ...) so that the key and arguments to the
            # key go in to self._outputdict['controls']
            return Robot.__add_attrs(
                key, __call__=lambda k, *args: self.__add(
                    k, args, calling_behaviour))

    @staticmethod
    def _get_behaviour(known_behaviours):
        calling_behaviour = None
        try:
            i = 0
            while True:
                caller = sys._getframe(i).f_code.co_name
                if caller in known_behaviours.keys():
                    calling_behaviour = caller
                    break
                i += 1
        except ValueError:
            # Indicates we hit the bottom of the stack without finding a
            # behaviour. This should never happen unless someone is mucking
            # around as all calls to the robot object should be from a
            # behaviour or a method called by a behaviour.
            pass
        return calling_behaviour

    @staticmethod
    def __add_attrs(obj, **kwargs):
        """ Allows the application of new attributes (to hold metadata etc) to
            existing types, including builtins like int/str.
        """
        try:
            obj.__dict__.update(kwargs)
            return obj
        except AttributeError:
            return type(obj.__class__.__name__,
                        (obj.__class__,),
                        kwargs)(obj)


class Memory(object):
    """ A "short term" memory object that you can read and write to.
    """
    def __init__(self, existing_memory={}):
        self.__memory = existing_memory

    @property
    def for_upload(self):
        return self.__memory

    @staticmethod
    def _valid(key, value):
        try:
            # Test that the key-value pair work in a dict and JSON
            test = {}
            test[key] = value
            json.dumps(test)
            return True
        except:
            return False

    def save(self, key, value):
        if not Memory._valid(key, value):
            raise Exception(
                'Cannot save key-value pair in memory: {} {}'.format(key, value))
        self.__memory[key] = value

    def load(self, key, default):
        if not Memory._valid(key, default):
            raise Exception(
                'Cannot load key-default pair from memory: {} {}'.format(key, default))
        if key not in self.__memory.keys():
            self.__memory[key] = default
        return self.__memory[key]

# Instanciate the memory object
memory = Memory(__MEMORY)

# Robot object to read and write to
robot = Robot(__output, __behaviours)

# Begin the code-wrapping try-except
try:
    # Using a class here allows for @behaviour etc decorators
    class RunnableRobot(object):
