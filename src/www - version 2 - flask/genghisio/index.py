"""

The desktop page

"""
from genghisio import app
from genghisio import socketio
import flask


@app.route('/')
def index():
    """ The default page that is loaded on the domain
    """
    return flask.render_template('index.html')
