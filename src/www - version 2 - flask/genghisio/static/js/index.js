// A blocker for execution
var emp_busy = true;

// Start the empythoned worker immediately
var emp_worker = new Worker('/static/emp/worker.js');

// Create the websocket connection back to the server
var api_socket = io.connect('http://' + document.domain + ':' + location.port + '/api');

// setInterval ids for (re-)registering the current session id
var sessionRegisterTimerIds = Array();

var code = null;
var memory = {};
var botId = null;

var dropzone = null;

function bumpSid() {
    $.get('/api/sid', function(data) {

        $('input[name="sessionId"]').val(data.sessionId);

        // Register the new session id. This is so we get the
        // notification back with the formatted code.
        api_socket.emit('register', {
            sessionId: data.sessionId,
        });

        // Ensure it re-registers fairly regularly in case the
        // server process dies... We don't want to register
        // for old sessions so we clear those first.
        $.each(sessionRegisterTimerIds, function(_, id) {
            clearInterval(id);
        });
        sessionRegisterTimerIds.push(setInterval(function() {
            api_socket.emit('register', {
                sessionId: data.sessionId,
            });
        }, 1000));
    });
}

$(document).ready(function() {
    bumpSid();

    // Hook up the dropzone
    dropzone = new Dropzone('#the_drop', {
        url: '/api/file',
        maxFilesize: 0.01,
        uploadMultiple: false,
        createImageThumbnails: false,
        maxFiles: 1,
        init: function() {
            this.on("sending", function(file, xhr, formData) {

                // Append the current session id
                formData.append("sessionId", $('input[name="sessionId"]').val());

                // Generate a new one for later
                bumpSid();

            });
        },
    });
    $('#icon_wrap').click(function() {
        $('#the_drop').click();
    });

    /*
        Trap pings to execute the code in Python.

        Object attributes:
            blacklist -- a list of methods not to call.
            inputs -- a list of inputs (TODO...)
    */
    api_socket.on('ping', function(data) {

        // Record the latest botId
        botId = data.botId;

        // We shouldn't be in this situation, but, people do funny
        // things :)
        if (code == null) {
            return;
        }

        // Prep the dynamic elements of the code
        var header = Array();
        header.push('__MEMORY = ' + JSON.stringify(memory));
        header.push('__INPUTS = (');
        for (var i in data.inputs) {
            continue; // TODO: parse input structure...
        }
        header.push(')');
        header.push('__BLACKLIST = (');
        $.each(data.blacklist, function(_, behaviour) {
            header.push('\'' + behaviour + '\',');
        });
        header.push(')');
        var gen_code = [header.join('\n'), code].join('\n');

        // If empythoned is busy, don't execute
        if (emp_busy == true) {
            return;
        }

        // Trigger the evaluation
        emp_busy = true;
        emp_worker.postMessage(gen_code);

    });

    /*
        Trap new debug messages from the code
    */
    api_socket.on('debug', function(json) {
        var line = '<div>';
        line += '[' + (new Date()).toLocaleTimeString() + '] ';
        line += 'Debug: ' + json.msg + '</div>';
        $('#debug').prepend(line);

        // Only keep 30 most recent messages
        $('#debug div').slice(30).remove();

    });

    /*
        Trap new code being sent to the user by the server.
    */
    api_socket.on('code', function(json) {

        // Clear the file input so we can do another upload later
       dropzone.removeAllFiles();

        // Show the filename. TODO: make sure funny names don't come
        // through...
        $('#current_filename').text('Loaded: ' + json.filename)

        // Update the QR code
        $('#qrcode').html('');
        $('#qrcode').qrcode({
            width: 100,
            height: 100,
            text: json.sessionId,
        });

        // Store the new code for execution
        code = json.src;
    });

    /*
        Trap messages fom empythoned
    */
    var empMessages = function(message) {
        switch (message.data.type) {
        case 'status':
            if (message.data.value == 'EMP_LOADED') {
                emp_busy = false;
            }
            break;
        case 'eval':
            emp_busy = false;
            try {
                // Get the generated nested JSON
                var json = JSON.parse(message.data.value);
            }
            catch(err) {
                // We're here because it wasn't valid JSON, so
                // a major syntax error etc. TODO: err, stop...
                console.log('Syntax err: ' + message.data.value);
                return;
            }

            // If we have errors here, they are runtime. Stop.
            // TODO: err, stop...
            if (json.errors != undefined) {
                console.log('Runtime err: ' + json.errors);
                return;
            }

            // Return the results to the server (and on to the
            // bot)
            api_socket.emit('control', {
                sessionId: $('input[name=sessionId]').val(),
                controls: json.controls,
                behaviours: json.behaviours,
                botId: botId,
            });
            break;
        }
    };
    emp_worker.addEventListener('message', empMessages, false);

});
