;(function () {

    // FF fix - otherwise sooks about "console not defined"
    self.console = {
        log: function () {}
    };

    // Buffer to hold responses
    var response = '';

    // Called once per character of output of eval, chr is a char code
    var charFunc = function(chr) {
        if (chr !== null) {
            // Add char to buffer
            response += String.fromCharCode(chr);
        }
    }

    // Called as a result of message sent from UI to worker.
    // 'e.data' contains the python code.
    var msgHandler = function (e) {

        // Eval the code. Any stdout characters are sent to charFunc.
        Python.eval(e.data);

        // Python.eval is *blocking* so we can send whatever was cached in
        // response by here, then clear the response.
        postMessage({type: 'eval', value: response});
        response = '';
    };

    // Import empythoned itself
    importScripts('/static/emp/python.opt.js');

    // Run it up the first time, register the function to handle characters
    // being returned.
    Python.initialize(null, charFunc);

    // This message is sent to indicate that eveything is ready - the
    // rest of the imports can happen in the background and are just
    // to speed stuff up later.
    postMessage({type: 'status', value: 'EMP_LOADED'});

    // Load a number of slow modules early so they don't hold up the first
    // ping we get from the bot.
    var code = ''
    var modules = ['random', 'json', 'sys', 'traceback'];
    for(i = 0; i < modules.length; i++) {
        code += 'import ' + modules[i] + '\n';
    };
    Python.eval(code);

    // Listen for messages that trigger the initial loading and the subsequent
    // execution of python code.
    addEventListener('message', msgHandler, false);

})();
