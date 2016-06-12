# Allow full imports from root of web app
import sys
sys.path.append('.')

# Fix for a threading exception http://stackoverflow.com/a/18455952/577190
if 'threading' in sys.modules:
    del sys.modules['threading']
import gevent
import gevent.socket
import gevent.monkey
gevent.monkey.patch_all()
