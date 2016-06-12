"""

Android embedded app pages.

"""
import jinja2
import os
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Home(webapp2.RequestHandler):
    """ The default page that is loaded in the android app's webview.
    """
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('android_home.html')
        self.response.write(template.render())


class Connect(webapp2.RequestHandler):
    """ The page that loaded while the android app attempts to connect to
        robot you selected on the previous (Home) page.
    """
    def get(self, botId):
        template = JINJA_ENVIRONMENT.get_template('android_connect.html')
        self.response.write(template.render({'botId': botId}))


class Controller(webapp2.RequestHandler):
    """ The page that you scan from and start/stop the bot.
    """
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('android_controller.html')
        self.response.write(template.render())


application = webapp2.WSGIApplication([
    ('/android', Home),
    ('/android/connect/(.*)', Connect),
    ('/android/ready', Controller),
], debug=True)
