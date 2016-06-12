import json
import os
import webapp2


class Format(webapp2.RequestHandler):
    """ The formatter for IDE-developed code.
    """
    BASE_PATH = os.path.dirname(__file__)
    INDENT = 8 # Spaces

    def _template(self, name):
        """ Loads a python template by name, returns it.
        """
        file_path = os.path.join(Format.BASE_PATH, name)
        with open(file_path, 'r') as f:
            return f.read()

    def post(self):
        """ Send this method a POST, containing a JSON object with string
            element 'code'.

            The contents of that method will be wrapped in appropriate code
            and returned as a JSON object with a 'formatted_code' element.
        """
        # Parse the json data
        json_data = json.loads(self.request.body)
        code = json_data['code']

        # Grab the header first, formatting the memory
        formatted_code = self._template('header.py')

        # Add each code line, indented twice
        for line in code.split('\n'):
            formatted_code += '{}{}\n'.format(' ' * Format.INDENT, line)

        # Add the footer
        formatted_code += self._template('footer.py')

        # Package it up
        json_result = json.dumps({'formatted_code': formatted_code})

        # And send it back
        self.response.write(json_result)
