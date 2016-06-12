import jinja2
import os
import tools
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class BotPage(webapp2.RequestHandler):

    def get(self, qr):
        if not tools.valid_qr(qr):
            return
        template = JINJA_ENVIRONMENT.get_template('bot.html')
        self.response.write(template.render({'qr': qr}))


application = webapp2.WSGIApplication([
    ('/bot/(.*)', BotPage),
])
