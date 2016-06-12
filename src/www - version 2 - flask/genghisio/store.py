"""

Methods and so-on for stuff that is (semi-)persistent.

"""
from genghisio import cache


def get_controls(id):
    """ Returns the controls for an id, or [] if none.
    """
    controls = cache.get('controls:{}'.format(id))
    if controls is None:
        controls = []
    return controls


def set_controls(id, controls):
    """ Sets the controls for an id.
    """
    cache.set('controls:{}'.format(id), controls)
