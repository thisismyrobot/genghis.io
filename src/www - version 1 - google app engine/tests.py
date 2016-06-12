import jinja2
import os
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Tests(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('tests/js/runner.html')
        self.response.write(template.render())


application = webapp2.WSGIApplication([
    ('/tests', Tests),
])
