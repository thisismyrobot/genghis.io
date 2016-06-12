/*
    Settings
*/
var mod='homepage';
var urlbase=window.location.origin;

/*
    Boilerplate
*/
module(mod, {
    setup: function() {
        F.timeout = 2;
    },
    teardown: function() {
        // Make sure we tidy up and close the window
        try {
            F.win.close();
        }
        catch(err) {};
    }
});

/*
    Tests
*/
test('Home page has an extra button to start developing', function() {
    F.open(urlbase);
    F('#develop_direct').visible(100, undefined, 'Missing "Get Started" button');
});
