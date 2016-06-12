# Flask fundamentals
from flask import Flask
app = Flask('genghisio')

# Some configuration
app.config['SECRET_KEY'] = 'secret!' # TODO: don't...
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 # 10KB seems fair

# Websockets
import flask.ext.socketio
socketio = flask.ext.socketio.SocketIO(app)

# Memcache
import werkzeug.contrib.cache
cache = werkzeug.contrib.cache.MemcachedCache(['127.0.0.1:11211'])

# The API to coordinate realtime control
import genghisio.api

# Android embedded page
import genghisio.android

# The homepage
import genghisio.index

# The JS tests!
import genghisio.test
