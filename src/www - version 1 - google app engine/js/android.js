var genghisio = {};

(function() {

    var sessionId = null;
    var pinging = false;

    this.BTFILTERS = {
        sphero: 'Sphero-[A-Z]{3}'
    };

    this.pingTicker = function() {
        setInterval(function() {
            if(sessionId === null) {
                return;
            }
            if(pinging === false) {
                return;
            }
            var result = Android.ping(sessionId);
        }, 1000);
    };

    this.go = function() {
        pinging = true;
    };

    this.stop = function() {
        pinging = false;
    };

    var showControls = function() {
        $('#go').removeAttr('disabled');
        $('#stop').removeAttr('disabled');
    };

    /*
        Namespace for functions that are called from Android parent app.
    */
    this.notify = {};
    (function() {

        this.newSid = function(newSessionId) {
            sessionId = newSessionId;
            showControls();
        };

        this.robotConnected = function() {
            window.location.href = '/android/ready';
        };

        this.robotConnectFail = function() {
            alert('Failed to connect...');
        };

    }).apply(this.notify);

}).apply(genghisio);
