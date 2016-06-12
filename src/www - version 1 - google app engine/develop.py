import jinja2
import os
import tools
import webapp2

from google.appengine.api import channel


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        app_id = 'genghis.io'
        client_id = tools.client_id()
        token = channel.create_channel(client_id)
        template = JINJA_ENVIRONMENT.get_template('develop.html')
        self.response.write(template.render({
            'token': token,
            'client_id': client_id,
        }))


application = webapp2.WSGIApplication([
    ('/develop', MainPage),
])
