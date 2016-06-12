var genghisio = {};

(function() {

    var controlSpeed = 200; // ms per control check
    var sessionId = null;
    var pinging = false;
    var controlQueue = new Array();

    this.BTFILTERS = {
        sphero: 'Sphero-[A-Z]{3}'
    };

    var ping = function(api_socket, sessionId, botId) {
        api_socket.emit('ping', {
            sessionId: sessionId,
            botId: botId,
            inputs: {},
        });
    };

    this.popError = function(message) {
        Android.toast(message);
    };

    /*
        Looks for new controls in the control queue, sending them to the bot.
    */
    this.controlTicker = function(botId) {
        setInterval(function() {

            // discard control queue if stopped
            if(pinging === false) {
                controlQueue = new Array();
                return;
            }

            // Don't do anything if we don't have any controls
            if (controlQueue.length == 0) {
                return;
            }

            // Get the control at the head of the queue
            var control = controlQueue.shift();

            // Display it for debug/presentation purposes
            $('#ctrl_scroll').prepend('<div>&gt; ' + control + '</div>');

            // Only keep 100 most recent messages, for the sake of DOM
            // memory...
            $('#ctrl_scroll div').slice(100).remove();

            // Send the control to Android
            try {
                Android.sendControl(control);
            }
            catch(err) {
                console.log(err);
            }

        }, controlSpeed);

    };

    /*
        Sets up the API socket to listen from controls, pings for new controls 
        regularly.
    */
    this.pingTicker = function(botId) {
        var api_socket = io.connect('http://' + document.domain + ':' + location.port + '/api');
        api_socket.on('control', function(message) {

            // discard new controls if stopped
            if(pinging === false) {
                return;
            }

            // Add new controls to back of queue
            controlQueue.push(message.control);

        });

        setInterval(function() {
            // Don't ping if we don't have a session id (qr code)
            if(sessionId === null) {
                return;
            }
            // Don't ping if we have pressed stop
            if(pinging === false) {
                return;
            }
            // Don't ping if we have heaps
            if (controlQueue.length > 3) {
                return;
            }
            ping(api_socket, sessionId, botId);
        }, controlSpeed / 4);
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

    this.connectRobot = function(botId, btFilter) {
        Android.connectRobot(botId, btFilter);
    };

    this.openUrl = function(url) {
        window.location.href = url;
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

        this.robotConnected = function(botId) {
            genghisio.openUrl('/android/ready/' + botId);
        };

        this.robotConnectError = function(message) {
            Android.toast('Robot connect error: ' + message);
            genghisio.openUrl('/android');
        };

    }).apply(this.notify);

}).apply(genghisio);
