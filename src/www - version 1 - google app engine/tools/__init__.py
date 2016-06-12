import hashlib
import os
import re


def client_id(random_bytes=256):
    """ Generates a unique client id for the request. A channel api token will
        be created off this id and this id will be used for channel messaging.

        I was using the token for this but the AppScale implementation had a
        massive sook at the length (it's limited to 64 bytes for a client id)
        whereas GAE is happy up to 256 bytes.
    """
    return hashlib.sha256(os.urandom(random_bytes)).hexdigest()

def valid_qr(text):
    """ Returns true if the text is a valid qr code, false otherwise.
    """
    return re.match('[a-f0-9]{40}', text) is not None
