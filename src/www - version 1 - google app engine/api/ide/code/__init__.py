import json
import logging
import os
import traceback
import webapp2


BASE_PATH = os.path.join(os.path.dirname(__file__), 'examples')

# A white-list of examples and their relative paths below 'examples'. The
# second element in the path tuples is an indicitive complexity from 1 (easy)
# to 5 (hard).
EXAMPLE_DATA = {
    # Generic examples
    (None, None): ('hello_world.py', 1),
    (None,'hello_world'): ('hello_world.py', 1),
    (None,'counter'): ('counter.py', 2),

    # BallBot examples - same as Sphero
    ('ballbot', None): (os.path.join('sphero', 'square.py'), 1),
    ('ballbot', 'square'): (os.path.join('sphero', 'square.py'), 1),
    ('ballbot', 'random'): (os.path.join('sphero', 'random.py'), 1),

    # Sphero examples
    ('sphero', None): (os.path.join('sphero', 'square.py'), 1),
    ('sphero', 'square'): (os.path.join('sphero', 'square.py'), 1),
    ('sphero', 'random'): (os.path.join('sphero', 'random.py'), 1),
}


META_LINES = 2


def load_example(path):
    file_path = os.path.join(BASE_PATH, path)
    with open(file_path, 'r') as f:
        return f.read().strip() + '\n'

def get_code(example):
    """ Returns just the code from an example.
    """
    return '\n'.join(example.split('\n')[META_LINES:])

def get_meta(example):
    """ Returns just the metadata from an example.
    """
    return map(lambda line: line[2:],
               example.split('\n')[:META_LINES])


class CodeExampleSummary(webapp2.RequestHandler):
    """ Returns list of code [title, summary, id] as JSON for a driverid.
    """
    def get(self, driver_id):

        # WSGI uses '' instead of None for no value in the URL
        if driver_id == '':
            driver_id = None

        # This will hold the resultant list of examples
        examples = []

        try:
            # Filter the examples by the driver id
            keys = filter(
                lambda key: key[0] == driver_id and key[1] is not None,
                EXAMPLE_DATA.keys())

            # Iterate the examples
            for key in keys:
                # Load the code metadata
                title, summary = get_meta(load_example(EXAMPLE_DATA[key][0]))

                # Load the difficulty
                difficulty = EXAMPLE_DATA[key][1]

                # Parse out the doc strings
                examples.append((difficulty, title, summary, key[1]))
        except:
            logging.error(traceback.format_exc())

        self.response.write(json.dumps({'examples': sorted(examples)}))


class CodeExample(webapp2.RequestHandler):
    """ Returns code examples by id, for a driver_id. If there is no code_id a
        default is returned. If there is no driverid, a 'hello world' example
        is returned.
    """
    def get(self):
        """ Call this method with (optionally) a driver id and code id GET
            param to get some suitable example code.
        """

        # Load hello world by default
        code = get_code(load_example(EXAMPLE_DATA[(None, None)][0]))

        try:
            code_id = self.request.get('code', '')
            driver_id = self.request.get('driver', '')

            if code_id == '':
                code_id = None
            if driver_id == '':
                driver_id = None

            key = (driver_id, code_id)

            # If the drive_id/code_id are funny - eg a path in the file
            # tree... - this will fail
            code_path = EXAMPLE_DATA[key][0]

            # If they are valid, but the code isn't where I said above, this
            # will fail
            code = get_code(load_example(code_path))
        except:
            logging.error(traceback.format_exc())

        self.response.write(json.dumps({'code': code}))
