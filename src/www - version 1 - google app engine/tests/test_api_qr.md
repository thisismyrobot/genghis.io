QR code generation
==================

Introduction
------------

The QR code module generates a QR code from a client_id passed to it. It also
saves that QR -> client_id mapping in memcached for later retrieval.

Bootstrap
---------

Generic setup.

    >>> import json
    >>> import webtest

Create a webtest API app.

    >>> import api
    >>> api = webtest.TestApp(api.application)

Tests
-----

Get QR code
~~~~~~~~~~~

The QR code is based on a client_id and the result is JSON.

    >>> client_id1 = 'testsetsetsetszt1234'
    >>> qr1 = json.loads(api.get('/api/qr/{}'.format(client_id1)).body)['qrcode']
    >>> qr1
    u'eba69dfacc9bc7a8364bfd879ea530e19b284c9d'

And is unique per client_id.

    >>> client_id2 = 'umerridontknow129389ew87r9873942'
    >>> qr2 = json.loads(api.get('/api/qr/{}'.format(client_id2)).body)['qrcode']
    >>> qr1 == qr2
    False

But stable.

    >>> qr3 = json.loads(api.get('/api/qr/{}'.format(client_id2)).body)['qrcode']
    >>> qr2 == qr3
    True

Stored QR codes
~~~~~~~~~~~~~~~

A QR codes -> client_ids map is stored in the memcache so that when a phone
connects using a QR code the client_id is retrievable. This should be the
*only* way to get a client_id from a QR code and is why the above process uses
one-way hashing to get the QR code.

    >>> import api.qr
    >>> api.qr.get_client_id(qr1) == client_id1
    True

    >>> api.qr.get_client_id(qr2) == client_id2
    True
