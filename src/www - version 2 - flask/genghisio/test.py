"""

The tests!!!

"""
from genghisio import app
from genghisio import socketio
import flask


@app.route('/test')
def test():
    """ The page that runs/shows the tests.
    """
    return flask.render_template('test.html')
