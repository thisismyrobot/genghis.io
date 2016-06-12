/*
    For PhantomJS headless testing

    Code here based 99.99% on https://github.com/ariya/phantomjs/blob/master/examples/run-qunit.js

    Assumes that the Google App Engine SDK is hosting on http://localhost:8080/tests.

    Usage:
        phantomjs.exe phantom_runner.js

*/
var BASEURL = 'http://localhost:8080/tests'

var system = require('system');

function waitFor(testFx, onReady, timeOutMillis) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3001, //< Default Max Timout is 3s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 100); //< repeat check every 250ms
};

var page = require('webpage').create();

page.onConsoleMessage = function(msg) {
    console.log(msg);
};

page.open(BASEURL, function(status){
    if (status !== "success") {
        console.log("Unable to access network");
        phantom.exit(1);
    } else {
        waitFor(function(){
            return page.evaluate(function(){
                var el = document.getElementById('qunit-testresult');
                if (el && el.innerText.match('completed')) {
                    return true;
                }
                return false;
            });
        }, function(){
            var failedNum = page.evaluate(function(){
                var el = document.getElementById('qunit-testresult');
                // Return the number of failed tests
                try {
                    return el.getElementsByClassName('failed')[0].innerHTML;
                } catch (e) { 
                }
                return 10000;
            });
            phantom.exit((parseInt(failedNum, 10) > 0) ? 1 : 0);
        });
    }
});
