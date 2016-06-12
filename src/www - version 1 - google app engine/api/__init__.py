import codeformatter
import coordinator
import ide.code
import qr
import webapp2


# Map the various /api/.* urls to their service modules
application = webapp2.WSGIApplication([
    ('/api/format', codeformatter.Format),
    ('/api/ping/(.*)/(.*)', coordinator.Ping),
    ('/api/stop/(.*)/(.*)', coordinator.Stop),
    ('/api/record/(.*)', coordinator.Recorder),
    ('/api/qr/(.*)', qr.QRGen),
    ('/api/ide/code', ide.code.CodeExample),
    ('/api/ide/code/(.*)', ide.code.CodeExampleSummary),
])
