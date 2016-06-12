"""

Android embedded app pages.

"""
from genghisio import app
import flask


@app.route('/android')
def home():
    """ The default page that is loaded in the android app's webview.
    """
    return flask.render_template('android_home.html')


@app.route('/android/connect/<botId>')
def connect(botId):
    """ Connect-to-bot, by botId, page.
    """
    kw = {
        'botId': botId,
    }
    return flask.render_template('android_connect.html', **kw)


@app.route('/android/ready/<botId>')
def controller(botId):
    kw = {
        'botId': botId,
    }
    return flask.render_template('android_controller.html', **kw)
