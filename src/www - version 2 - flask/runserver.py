from genghisio import app
from genghisio import socketio


# Enables printed errors and Android mocks
app.debug = True

socketio.run(app, host='0.0.0.0', port=8080)
