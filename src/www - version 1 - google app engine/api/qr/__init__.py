import base64
import hashlib
import json
import webapp2

from google.appengine.api import memcache


def get_client_id(qrcode):
    """ Returns the client_id for a QR code from memcache or None if the
        qrcode is unknown.
    """
    return memcache.get('QR-{}'.format(qrcode))


class QRGen(webapp2.RequestHandler):
    """ Returns QR codes for client_ids. The QR code is based on a hash so is
        only one-way. The map is stored in memcache for later retrieval during
        a ping.

        The hashing is used for two reasons:
            a) The hash is a unique but shorter representation of the
               client_id
            b) It's one thing to send a client_id back and forth over SSL,
               it's another to print the client_id on the screen as a QR
               code...
    """
    def get(self, client_id):
        """ Send this method a client_id as part of the URL and you'll get a
            string to use in a qr code.

            As the QR -> client_id code map is only stored in memcache it's
            recommended you call this once every couple of seconds.
        """
        # Generate a qr code using hashing
        qrcode = hashlib.sha1(client_id).hexdigest()

        # Save the qr-code -> client_id map in memcache
        key = 'QR-{}'.format(qrcode)
        memcache.set(key, client_id)

        self.response.write(json.dumps({'qrcode': qrcode}))
