/*
    Basic mocks around the Android/iOS app for on-PC testing.

    android_genghisio should be populated in the global scope from the namespace in
    the the android contentwindow
*/
var Android = {};

(function() {

    // Update to set the QR that will be set.
    this.nextQR = '1234';

    this.frameLoaded = function() {
        console.log('Android.frameLoaded()');
    };

    this.connectRobot = function(bluetoothFilter) {
        console.log('Android.connectRobot(' + bluetoothFilter + ')');
        setTimeout(function() {
            android_genghisio.notify.robotConnected('sphero');
        }, 3000);
    };

    this.scanQR = function() {
        console.log('Android.scanQR()');
        var qr = this.nextQR;
        setTimeout(function() {
            android_genghisio.notify.newSid(qr);
        }, 500);
    };

    this.sendControl = function(control) {
        console.log('Android.sendControl(' + control + ')');
    };

    this.toast = function(message) {
        console.log('Android.toast(' + message + ')');
    };

}).apply(Android);
