/*

    Sync testrunner with delays.

    These are delays between individual QUnit tests to allow for less nesting
    when doing handover to next tests etc.

*/
var genghisio = {};
(function() {
    this.tests = {};
    (function() {
        var step = function(queue) {
            var head = queue.pop();
            switch(typeof(head)) {
                case 'function':
                    head();
                    step(queue);
                    break;
                case 'number':
                    setTimeout(function() {
                        step(queue);
                    }, head);
                    break;
            }
        };
        this.run = function() {
            var queue = Array();
            for (i in arguments) {
                queue.push(arguments[i]);
            }
            step(queue.reverse());
        };
    }).apply(this.tests);
}).apply(genghisio);

// Things that will last between tests.
var androidIframe, browserIframe, connectButton, goButton, stopButton, scanButton, sid;

/*
    Run the actual tests.
*/
genghisio.tests.run(
    // Wait for everything to load
    2000,

    // Do some setup
    function() {
        // Find a couple of elements that we'll use a lot
        androidIframe = document.getElementById('android_frame');
        browserIFrame = document.getElementById('browser_frame');
        connectButton = $(androidIframe).contents().find('input[type="button"][value="Connect"]');
    },

    // There's a cool session id generating api endpoint, that generates
    // random 40 character (hex) strings every time we go to it.
    function() {
        QUnit.asyncTest('Session ID api works', function(assert) {
            expect(2);

            $.get('/api/sid', function(data) {
                sid = data.sessionId;
                assert.equal(sid.length, 40,
                    'Session IDs are 40 characters');

                $.get('/api/sid', function(data) {
                    var sid2 = data.sessionId;
                    assert.notEqual(sid, sid2,
                        'Session IDs are different per call');
                    QUnit.start();
                });
            });
        });
    },

    // Check for a connect button in the android webframe
    function() {
        QUnit.test('There\'s a connect button', function(assert) {
            assert.equal(connectButton.length, 1, 'Connect button exists');
            connectButton.click();
            assert.ok(true, 'Connect button is clickable');
        });
    },

    // Wait for the connect page to load
    1500,

    // Check it's loaded
    function() {
        QUnit.test('Connect button redirects', function(assert) {
            var iframeUrl = $(androidIframe).attr('src');
            assert.equal(iframeUrl, "/android/connect/sphero");
        });
    },

    // Wait for the connection notification mock to load
    3500,

    // We should have the live page now
    function() {
        QUnit.test('Controls start disabled', function(assert) {
            goButton = $(androidIframe).contents().find(
                'input[type="button"][value="Go"]');
            stopButton = $(androidIframe).contents().find(
                'input[type="button"][value="Stop"]');
            assert.equal(stopButton.attr('disabled'), 'disabled');
            assert.equal(goButton.attr('disabled'), 'disabled');
        });
    },

    // Probably a good time to upload a file
    function() {
        QUnit.test('Can upload a file', function(assert) {

            var codeRx = false;

            // Create a valid upload
            var code = [
                '@behaviour(priority=1)',
                'def waltz():',
                '    debug(\'Starting waltz\')',
                '    robot.move_forwards(64)',
                '    wait(2)',
                '    robot.stop()',
                '    robot.move_left(64)',
                '    robot.stop()',
            ].join('\n');
            var data = new FormData();
            data.append(
                'file',
                new Blob([code], { type: 'text/plain' }),
                'sphero_test_code.py'
            );

            // Including the valid session id
            data.append('sessionId', sid);

            // Register the new session id with the mocks and the desktop
            // browser frame
            Android.nextQR = sid;
            $(browserIFrame).contents().find('input[name=sessionId]').val(sid);

            browserIFrame.contentWindow['api_socket'].emit(
                'register',
                {
                    sessionId: sid
                },
                function() {
                    // Perform the upload
                    $.ajax({
                        url: '/api/file',
                        data: data,
                        cache: false,
                        contentType: false,
                        processData: false,
                        type: 'POST'
                    });
                }
            );

            expect(0);
        });
    },

    // And we can click a Scan button
    function() {
        QUnit.test('Scan button causes scan', function(assert) {
            scanButton = $(androidIframe).contents().find(
                'input[type="button"][value="Scan"]');
            assert.equal(scanButton.attr('disabled'), undefined);
            scanButton.click();
        });
    },

    // Wait for the QR code to be returned
    2000,

    // Now the controls are enabled
    function() {
        QUnit.test('QR code enables controls', function(assert) {
            assert.equal(stopButton.attr('disabled'), undefined);
            assert.equal(goButton.attr('disabled'), undefined);
        });
    },

    1000,

    function() {
        goButton.click();
    },

0);
